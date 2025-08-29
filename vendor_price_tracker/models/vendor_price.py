# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class VendorPrice(models.Model):
    _name = 'vendor.price'
    _description = 'Vendor Price'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'product_id, partner_id, valid_from desc'
    _rec_name = 'display_name'

    display_name = fields.Char(compute='_compute_display_name', store=True)

    company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)
    currency_id = fields.Many2one(related='company_id.currency_id', store=True, readonly=True)

    product_id = fields.Many2one('product.product', required=True, index=True, tracking=True)
    partner_id = fields.Many2one(
        'res.partner', required=True, index=True, tracking=True,
        domain="[('supplier_rank','>',0)]", string='Vendor'
    )
    price = fields.Monetary(required=True, currency_field='currency_id', tracking=True)
    valid_from = fields.Date(required=True, default=fields.Date.context_today, tracking=True)
    valid_to = fields.Date()
    notes = fields.Text()

    is_current = fields.Boolean(compute='_compute_is_current', search='_search_is_current')
    is_expiring_30 = fields.Boolean(compute='_compute_is_expiring_30', search='_search_is_expiring_30')

    _sql_constraints = [
        ('uniq_vendor_price', 'unique(product_id, partner_id, valid_from, company_id)',
         'A vendor price with the same product, vendor, company and start date already exists.'),
    ]

    @api.depends('product_id', 'partner_id', 'valid_from')
    def _compute_display_name(self):
        for rec in self:
            if rec.product_id and rec.partner_id:
                rec.display_name = f"{rec.product_id.display_name} - {rec.partner_id.display_name} ({rec.valid_from})"
            else:
                rec.display_name = _('Vendor Price')

    @api.depends('valid_from', 'valid_to')
    def _compute_is_current(self):
        today = fields.Date.context_today(self)
        for rec in self:
            if not rec.valid_from:
                rec.is_current = False
                continue
            if rec.valid_to:
                rec.is_current = rec.valid_from <= today <= rec.valid_to
            else:
                rec.is_current = rec.valid_from <= today

    @api.depends('valid_to')
    def _compute_is_expiring_30(self):
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=30)
        for rec in self:
            rec.is_expiring_30 = bool(rec.valid_to and today <= rec.valid_to <= horizon)

    def _search_is_expiring_30(self, operator, value):
        today = fields.Date.context_today(self)
        horizon = today + timedelta(days=30)
        domain_exp = [('valid_to', '>=', today), ('valid_to', '<=', horizon)]
        if (operator in ('=', '==') and bool(value)) or (operator in ('!=', '<>') and not bool(value)):
            return domain_exp
        else:
            return ['!', ('id', 'in', self.search(domain_exp).ids)]

    @api.constrains('valid_from', 'valid_to')
    def _check_dates(self):
        for rec in self:
            if rec.valid_to and rec.valid_to < rec.valid_from:
                raise ValidationError(_('Valid To must be greater than or equal to Valid From.'))

    def name_get(self):
        return [(rec.id, rec.display_name or _('Vendor Price')) for rec in self]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Optional notification: new best price
        records._notify_new_best_price()
        return records

    def write(self, vals):
        res = super().write(vals)
        self._notify_new_best_price()
        return res

    def _search_is_current(self, operator, value):
        # Support search on is_current computed field
        today = fields.Date.context_today(self)
        domain_current = ['&', ('valid_from', '<=', today), '|', ('valid_to', '=', False), ('valid_to', '>=', today)]
        if (operator in ('=', '==') and bool(value)) or (operator in ('!=', '<>') and not bool(value)):
            return domain_current
        else:
            return ['!', ('id', 'in', self.search(domain_current).ids)]

    def _notify_new_best_price(self):
        # Post on product when a new lower current price appears and notify managers
        for rec in self:
            product = rec.product_id
            today = fields.Date.context_today(self)
            # Consider current prices including this record
            prices = product.vpt_price_ids.filtered(lambda p: p.company_id == product.company_id and p.valid_from and p.valid_from <= today and (not p.valid_to or p.valid_to >= today))
            if not prices:
                continue
            best = min(prices.mapped('price'))
            if rec.price == best:
                # New best price detected
                msg = _('New best vendor price: %s at %s from %s') % (
                    rec.partner_id.display_name,
                    product.currency_id.symbol + (' %.2f' % rec.price),
                    rec.valid_from,
                )
                managers = self.env.ref('vendor_price_tracker.group_vpt_manager', raise_if_not_found=False)
                partner_ids = managers.users.mapped('partner_id').ids if managers else []
                product.message_post(body=msg, partner_ids=partner_ids, subtype_xmlid='mail.mt_note')

    def action_open_product(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'form',
            'res_id': self.product_id.id,
            'target': 'current',
        }


    def cron_post_expired_prices(self):
        """Daily cron at 06:00: post chatter on products for prices that expired yesterday.
        is_current is computed, so no explicit flagging is required beyond notifying.
        """
        today = fields.Date.context_today(self)
        yesterday = today - timedelta(days=1)
        expired = self.search([('valid_to', '=', yesterday)])
        if not expired:
            return True
        by_product = {}
        for vp in expired:
            by_product.setdefault(vp.product_id, self.env['vendor.price'])
            by_product[vp.product_id] |= vp
        for product, lines in by_product.items():
            body = _('The following vendor prices expired on %s:') % yesterday
            for vp in lines:
                body += '<br/>- %s: %s %s (from %s to %s)' % (
                    vp.partner_id.display_name,
                    vp.currency_id.symbol,
                    '%.2f' % vp.price,
                    vp.valid_from,
                    vp.valid_to or ''
                )
            product.message_post(body=body)
        return True
