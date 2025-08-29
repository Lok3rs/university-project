# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError


EXPECTED_COLUMNS = ['product_default_code', 'vendor_name', 'price', 'valid_from', 'valid_to']


class VptCsvImportLine(models.TransientModel):
    _name = 'vpt.csv.import.line'
    _description = 'Vendor Price CSV Import Line'

    wizard_id = fields.Many2one('vpt.csv.import.wizard', required=True, ondelete='cascade')
    row_number = fields.Integer(readonly=True)

    product_default_code = fields.Char(readonly=True)
    vendor_name = fields.Char(readonly=True)
    price = fields.Float(readonly=True)
    valid_from = fields.Date(readonly=True)
    valid_to = fields.Date(readonly=True)

    product_id = fields.Many2one('product.product', readonly=True)
    partner_id = fields.Many2one('res.partner', readonly=True)

    action = fields.Selection([('create', 'Create'), ('update', 'Update'), ('skip', 'Skip')], default='create', readonly=True)
    status = fields.Selection([('ok', 'OK'), ('error', 'Error')], default='ok', readonly=True)
    message = fields.Char(readonly=True)


class VptCsvImportWizard(models.TransientModel):
    _name = 'vpt.csv.import.wizard'
    _description = 'Vendor Price CSV Import Wizard'

    data_file = fields.Binary(string='CSV File', required=True)
    filename = fields.Char()
    line_ids = fields.One2many('vpt.csv.import.line', 'wizard_id', string='Lines')
    state = fields.Selection([('draft', 'Draft'), ('preview', 'Preview'), ('done', 'Done')], default='draft')
    summary = fields.Text(readonly=True)

    def _decode_csv(self):
        self.ensure_one()
        try:
            data = base64.b64decode(self.data_file)
        except Exception:
            raise UserError(_('Could not decode the uploaded file.'))
        try:
            text = data.decode('utf-8')
        except UnicodeDecodeError:
            text = data.decode('latin-1')
        return io.StringIO(text)

    def action_preview(self):
        self.ensure_one()
        # reset previous lines
        self.line_ids.unlink()
        f = self._decode_csv()
        reader = csv.DictReader(f)
        missing = [c for c in EXPECTED_COLUMNS if c not in reader.fieldnames]
        if missing:
            raise UserError(_('Missing required columns: %s') % ', '.join(missing))
        lines = self.env['vpt.csv.import.line']
        rowno = 1
        for row in reader:
            rowno += 1
            vals = {
                'wizard_id': self.id,
                'row_number': rowno,
                'product_default_code': (row.get('product_default_code') or '').strip(),
                'vendor_name': (row.get('vendor_name') or '').strip(),
            }
            # parse price
            msg = ''
            status = 'ok'
            try:
                vals['price'] = float(row.get('price') or 0.0)
            except Exception:
                status, msg = 'error', _('Invalid price')
            # parse dates
            dt_format = '%Y-%m-%d'
            try:
                vals['valid_from'] = datetime.strptime((row.get('valid_from') or '').strip(), dt_format).date()
            except Exception:
                status, msg = 'error', _('Invalid valid_from (expected YYYY-MM-DD)')
            valid_to_str = (row.get('valid_to') or '').strip()
            if valid_to_str:
                try:
                    vals['valid_to'] = datetime.strptime(valid_to_str, dt_format).date()
                except Exception:
                    status, msg = 'error', _('Invalid valid_to (expected YYYY-MM-DD)')
            # find product
            product = self.env['product.product'].search([('default_code', '=', vals['product_default_code'])], limit=1)
            if not product:
                status, msg = 'error', _('Product not found')
            # find vendor
            partner = self.env['res.partner'].search([('name', '=', vals['vendor_name']), ('supplier_rank', '>', 0)], limit=1)
            if not partner:
                status, msg = 'error', _('Vendor not found or not a supplier')
            if status == 'ok' and vals.get('valid_to') and vals['valid_to'] < vals['valid_from']:
                status, msg = 'error', _('valid_to is before valid_from')
            vals['status'] = status
            vals['message'] = msg
            vals['product_id'] = product.id if product else False
            vals['partner_id'] = partner.id if partner else False
            # check existing
            action = 'create'
            if status == 'ok':
                existing = self.env['vendor.price'].search([
                    ('product_id', '=', product.id),
                    ('partner_id', '=', partner.id),
                    ('valid_from', '=', vals['valid_from']),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if existing:
                    action = 'update'
            vals['action'] = action
            lines |= lines.create(vals)
        self.state = 'preview'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vpt.csv.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def action_import(self):
        self.ensure_one()
        created = updated = errors = 0
        for line in self.line_ids:
            if line.status != 'ok':
                errors += 1
                continue
            vals = {
                'product_id': line.product_id.id,
                'partner_id': line.partner_id.id,
                'price': line.price,
                'valid_from': line.valid_from,
                'valid_to': line.valid_to,
                'company_id': self.env.company.id,
            }
            if line.action == 'update':
                rec = self.env['vendor.price'].search([
                    ('product_id', '=', line.product_id.id),
                    ('partner_id', '=', line.partner_id.id),
                    ('valid_from', '=', line.valid_from),
                    ('company_id', '=', self.env.company.id),
                ], limit=1)
                if rec:
                    rec.write(vals)
                    updated += 1
                else:
                    self.env['vendor.price'].create(vals)
                    created += 1
            else:
                self.env['vendor.price'].create(vals)
                created += 1
        self.summary = _('Created: %s\nUpdated: %s\nErrors: %s') % (created, updated, errors)
        self.state = 'done'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'vpt.csv.import.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
