# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    vpt_price_ids = fields.One2many('vendor.price', 'product_id', string='Vendor Prices')
    vpt_best_vendor_id = fields.Many2one('res.partner', compute='_compute_vpt_best_fields', store=False)
    vpt_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True)
    vpt_best_price = fields.Monetary(compute='_compute_vpt_best_fields', currency_field='vpt_currency_id', store=False)
    vpt_price_count = fields.Integer(compute='_compute_vpt_best_fields')

    @api.depends('vpt_price_ids.price', 'vpt_price_ids.valid_from', 'vpt_price_ids.valid_to', 'vpt_price_ids.partner_id', 'company_id')
    def _compute_vpt_best_fields(self):
        today = fields.Date.context_today(self)
        for product in self:
            prices = product.vpt_price_ids.filtered(lambda p: p.company_id == product.company_id and p.valid_from and p.valid_from <= today and (not p.valid_to or p.valid_to >= today))
            product.vpt_price_count = len(prices)
            if prices:
                best = prices.sorted(key=lambda p: p.price)[0]
                product.vpt_best_price = best.price
                product.vpt_best_vendor_id = best.partner_id
            else:
                product.vpt_best_price = False
                product.vpt_best_vendor_id = False

    def action_open_vendor_prices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Vendor Prices'),
            'res_model': 'vendor.price',
            'view_mode': 'tree,form,graph,pivot',
            'domain': [('product_id', '=', self.id)],
            'context': {
                'search_default_current': 1,
                'default_product_id': self.id,
            },
        }

    def action_compare_vendor_prices(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Compare Vendor Prices'),
            'res_model': 'vendor.price',
            'view_mode': 'pivot,graph,tree',
            'domain': [('product_id', '=', self.id)],
            'context': {
                'search_default_current': 1,
                'default_product_id': self.id,
                'pivot_measures': ['price:sum'],
                'graph_measure': 'price',
                'graph_groupbys': ['partner_id'],
                'limit': 5,
            },
            'target': 'current',
        }
