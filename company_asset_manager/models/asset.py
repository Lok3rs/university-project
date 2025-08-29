# -*- coding: utf-8 -*-
"""Company Asset Manager models.

Asset model with services and utilities; includes CSV export and scheduling helpers.
"""

import base64
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import AccessError


class CompanyAsset(models.Model):
    """Company asset with service scheduling and assignment."""
    _name = 'company.asset'
    _description = 'Company Asset'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Asset Name', required=True, tracking=True)
    category = fields.Selection(
        selection=[('laptop', 'Laptop'), ('phone', 'Phone'), ('networking', 'Networking'), ('other', 'Other')],
        required=True,
        tracking=True,
        index=True,
    )
    serial_no = fields.Char(string='Serial Number', index=True, tracking=True)
    purchase_date = fields.Date(string='Purchase Date', tracking=True)
    warranty_months = fields.Integer(string='Warranty (Months)', default=24)
    status = fields.Selection(
        selection=[('in_use', 'In Use'), ('in_service', 'In Service'), ('retired', 'Retired')],
        string='Status',
        default='in_use',
        tracking=True,
        index=True,
    )
    employee_id = fields.Many2one('hr.employee', string='Assigned To', tracking=True)

    service_interval_months = fields.Integer(string='Service Interval (Months)', default=6)
    next_service_date = fields.Date(string='Next Service Date', compute='_compute_next_service_date', store=True)

    notes = fields.Text(string='Notes')

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True, index=True)

    service_ids = fields.One2many('company.asset.service', 'asset_id', string='Services')
    service_count = fields.Integer(string='Services Count', compute='_compute_service_count')

    _sql_constraints = [
        ('serial_no_unique', 'unique(serial_no)', 'Serial number must be unique.'),
    ]

    @api.depends('service_ids.service_date', 'service_interval_months', 'purchase_date')
    def _compute_next_service_date(self):
        """Compute next service date based on last service or purchase date and interval."""
        for asset in self:
            interval = asset.service_interval_months or 0
            base_date = None
            # determine last service date
            if asset.service_ids:
                last = max(asset.service_ids.mapped('service_date') or [])
                base_date = last
            if not base_date:
                base_date = asset.purchase_date
            if base_date and interval:
                # relativedelta handles month arithmetic
                asset.next_service_date = fields.Date.to_date(base_date) + relativedelta(months=interval)
            else:
                asset.next_service_date = False

    @api.depends('service_ids')
    def _compute_service_count(self):
        """Compute number of related service records for each asset."""
        counts = {}
        if self.ids:
            groups = self.env['company.asset.service'].read_group(
                [('asset_id', 'in', self.ids)], ['asset_id'], ['asset_id']
            )
            counts = {g['asset_id'][0]: g['asset_id_count'] for g in groups}
        for asset in self:
            asset.service_count = counts.get(asset.id, 0)

    def action_view_services(self):
        """Open services related to the asset with default domain/context."""
        self.ensure_one()
        action = self.env.ref('company_asset_manager.action_company_asset_services').read()[0]
        action['domain'] = [('asset_id', '=', self.id)]
        action['context'] = {'default_asset_id': self.id}
        return action

    def action_view_attachments(self):
        """Open attachments linked to this asset."""
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('res_model', '=', self._name), ('res_id', '=', self.id)],
            'context': {'default_res_model': self._name, 'default_res_id': self.id},
            'target': 'current',
        }

    def action_assign_wizard(self):
        """Open assignment wizard prefilled with the current asset."""
        self.ensure_one()
        return {
            'name': _('Assign to Employee'),
            'type': 'ir.actions.act_window',
            'res_model': 'company.asset.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_asset_id': self.id,
            },
        }

    def _get_export_fields_for_csv(self):
        """Return the fields to include in exported CSV (technical names)."""
        return ['name', 'serial_no', 'category', 'employee_id', 'status', 'next_service_date']

    def action_export_csv(self):
        """Export selected (or all) assets to CSV and return a download URL."""
        # Managers only
        if not self.env.user.has_group('company_asset_manager.group_asset_manager'):
            raise AccessError(_('Only managers can export assets.'))
        # Prepare data
        records = self if self else self.search([])
        headers = ['Name', 'Serial', 'Category', 'Employee', 'Status', 'Next Service Date']
        lines = [','.join('"%s"' % h for h in headers)]
        for rec in records:
            vals = [
                rec.name or '',
                rec.serial_no or '',
                dict(self._fields['category'].selection).get(rec.category or '', '') or '',
                rec.employee_id.name or '',
                dict(self._fields['status'].selection).get(rec.status or '', '') or '',
                rec.next_service_date and fields.Date.to_string(rec.next_service_date) or '',
            ]
            # Escape quotes per CSV conventions
            lines.append(','.join('"%s"' % (v.replace('"', '""')) for v in vals))
        content = '\n'.join(lines)
        # Create attachment
        filename = 'assets_export_%s.csv' % fields.Date.to_string(fields.Date.context_today(self))
        data = content.encode('utf-8')
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(data),
            'mimetype': 'text/csv',
            'res_model': 'company.asset',
            'public': False,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }


class CompanyAssetService(models.Model):
    _name = 'company.asset.service'
    _description = 'Asset Service'
    _order = 'service_date desc, id desc'

    asset_id = fields.Many2one('company.asset', string='Asset', required=True, ondelete='cascade', index=True)
    service_date = fields.Date(string='Service Date', default=lambda self: fields.Date.context_today(self), required=True)
    description = fields.Text(string='Description')
    cost = fields.Monetary(string='Cost')
    currency_id = fields.Many2one('res.currency', string='Currency', related='asset_id.company_id.currency_id', store=True, readonly=True)

    company_id = fields.Many2one(related='asset_id.company_id', store=True, readonly=True)


    @api.model
    def _cron_schedule_upcoming_services(self):
        today = fields.Date.today()
        deadline = today + relativedelta(days=14)
        assets = self.search([
            ('next_service_date', '!=', False),
            ('next_service_date', '<=', deadline),
            ('status', '!=', 'retired'),
        ])
        if not assets:
            return True
        # Post chatter log and schedule activities for all Asset Managers
        try:
            mgr_group = self.env.ref('company_asset_manager.group_asset_manager')
            users = mgr_group.users
        except Exception:
            users = self.env['res.users']
        for asset in assets:
            # Log once per run
            try:
                asset.message_post(body=_('Upcoming service due on %(date)s.', date=fields.Date.to_string(asset.next_service_date)))
            except Exception:
                pass
            for user in users:
                # Avoid duplicate activities for same user/asset/summary
                existing = self.env['mail.activity'].search([
                    ('res_model', '=', asset._name),
                    ('res_id', '=', asset.id),
                    ('user_id', '=', user.id),
                    ('summary', '=', 'Upcoming service'),
                ], limit=1)
                if existing:
                    continue
                try:
                    asset.activity_schedule(
                        act_type_xmlid='mail.mail_activity_data_todo',
                        date_deadline=asset.next_service_date or today,
                        summary=_('Upcoming service'),
                        note=_('Asset %(name)s requires service by %(date)s.', name=asset.name, date=fields.Date.to_string(asset.next_service_date or today)),
                        user_id=user.id,
                    )
                except Exception:
                    pass
        return True
