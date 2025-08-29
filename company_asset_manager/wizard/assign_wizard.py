# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class AssetAssignWizard(models.TransientModel):
    _name = 'company.asset.assign.wizard'
    _description = 'Assign Asset to Employee Wizard'

    asset_id = fields.Many2one('company.asset', string='Asset', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    note = fields.Text(string='Note')

    def action_confirm(self):
        self.ensure_one()
        asset = self.asset_id
        old_emp = asset.employee_id
        asset.write({'employee_id': self.employee_id.id})
        message = _('Asset assigned to %s') % (self.employee_id.name)
        if self.note:
            message += _('\nNote: %s') % self.note
        if old_emp:
            message = _('Reassigned from %s to %s.') % (old_emp.name, self.employee_id.name) + ('\n' + self.note if self.note else '')
        asset.message_post(body=message)
        return {'type': 'ir.actions.act_window_close'}
