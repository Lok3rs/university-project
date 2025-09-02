# -*- coding: utf-8 -*-
"""Helpdesk Lite models.

Provides a simple helpdesk ticket model with portal support, CSV export, and SLA checks.
"""

import base64
import csv
import io
import logging
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)


class HelpdeskTicket(models.Model):
    """Basic helpdesk/ticket model for Odoo Community.

    Features:
    - Chatter & activities via mail.thread and mail.activity.mixin
    - Portal support via portal.mixin for access URLs
    - SLA overdue cron helper
    - Email notification on stage change
    - CSV export action for managers
    """

    _name = 'helpdesk.ticket'
    _description = 'Helpdesk Ticket'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'priority desc, id desc'

    name = fields.Char(string='Title', required=True, tracking=True)
    description = fields.Text(string='Description')
    partner_id = fields.Many2one('res.partner', string='Customer', tracking=True)
    assignee_id = fields.Many2one('res.users', string='Assignee', tracking=True)
    priority = fields.Selection(
        selection=[('0', 'Low'), ('1', 'Normal'), ('2', 'High')],
        string='Priority', default='1', index=True, tracking=True,
    )
    stage = fields.Selection(
        selection=[
            ('new', 'New'),
            ('in_progress', 'In Progress'),
            ('waiting', 'Waiting'),
            ('done', 'Done'),
        ],
        string='Stage', default='new', index=True, tracking=True,
    )
    channel = fields.Selection(
        selection=[('email', 'Email'), ('phone', 'Phone'), ('portal', 'Portal'), ('other', 'Other')],
        string='Channel', tracking=True,
    )
    attachment_count = fields.Integer(string='Attachments', compute='_compute_attachment_count')
    sla_deadline = fields.Datetime(string='SLA Deadline')
    closed_date = fields.Datetime(string='Closed Date', copy=False)

    # ---------------------------------------------------------------------
    # COMPUTES / CONSTRAINTS / ONCHANGE
    # ---------------------------------------------------------------------
    @api.constrains('name')
    def _check_name_length(self) -> None:
        """Validate that the title is longer than 3 characters.

        Raises:
            ValidationError: If the title is missing or too short.
        """
        for ticket in self:
            if not ticket.name or len(ticket.name.strip()) <= 3:
                raise ValidationError(_('The ticket title must be longer than 3 characters.'))

    def _compute_attachment_count(self) -> None:
        """Compute the number of attachments per ticket using read_group."""
        # Using read_group for batch compute
        counts = {}
        if self.ids:
            data = self.env['ir.attachment'].read_group(
                [('res_model', '=', 'helpdesk.ticket'), ('res_id', 'in', self.ids)],
                ['res_id'], ['res_id']
            )
            counts = {d['res_id']: d['res_id_count'] for d in data}
        for rec in self:
            rec.attachment_count = counts.get(rec.id, 0)

    @api.onchange('stage')
    def _onchange_stage(self) -> None:
        """When stage becomes done, set closed_date if missing."""
        for ticket in self:
            if ticket.stage == 'done' and not ticket.closed_date:
                ticket.closed_date = fields.Datetime.now()

    def write(self, vals) -> bool:
        """Write changes to tickets and notify on stage change.

        Detect stage changes to send an email notification via template and
        ensure closed_date is set when moving to Done.

        Args:
            vals: Values to write.

        Returns:
            bool: Result from super().write(vals).
        """
        # Detect stage changes before write
        stage_changed_ids = []
        if 'stage' in vals:
            for t in self:
                if t.stage != vals.get('stage'):
                    stage_changed_ids.append(t.id)
        res = super().write(vals)
        if stage_changed_ids:
            template = self.env.ref('helpdesk_lite.mail_template_ticket_stage_update', raise_if_not_found=False)
            if template:
                for ticket in self.browse(stage_changed_ids):
                    # ensure closed_date set on done in write context as well
                    if ticket.stage == 'done' and not ticket.closed_date:
                        ticket.closed_date = fields.Datetime.now()
                    try:
                        template.send_mail(ticket.id, force_send=True)
                    except Exception:
                        # avoid breaking write due to email errors
                        pass
        return res

    # ---------------------------------------------------------------------
    # PORTAL MIXIN
    # ---------------------------------------------------------------------
    def _compute_access_url(self) -> None:
        """Compute the portal access URL for each ticket."""
        super()._compute_access_url()
        for ticket in self:
            ticket.access_url = '/my/helpdesk/%s' % ticket.id

    # ---------------------------------------------------------------------
    # ACTIONS / REPORTING HELPERS
    # ---------------------------------------------------------------------
    def action_start_progress(self):
        """Set ticket to In Progress stage.

        - If currently done, also clear closed_date to reopen.
        - Post a message to the chatter.
        """
        for t in self:
            vals = {'stage': 'in_progress'}
            if t.stage == 'done' and t.closed_date:
                vals['closed_date'] = False
            t.write(vals)
            t.message_post(body=_('Ticket moved to In Progress.'))
        return True

    def action_put_waiting(self):
        """Set ticket to Waiting stage and post a chatter message."""
        for t in self:
            # Do not alter closed_date here; only done stage sets it.
            t.write({'stage': 'waiting'})
            t.message_post(body=_('Ticket put to Waiting.'))
        return True

    def action_mark_done(self):
        """Set ticket to Done stage and set Closed Date to now.

        Even though write/onchange fills it, we ensure it explicitly here for clarity.
        """
        now = fields.Datetime.now()
        for t in self:
            t.write({'stage': 'done', 'closed_date': now})
            t.message_post(body=_('Ticket marked as Done at %(dt)s.', dt=now))
        return True

    def action_view_attachments(self):
        self.ensure_one()
        return {
            'name': _('Attachments'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'tree,form',
            'domain': [('res_model', '=', 'helpdesk.ticket'), ('res_id', '=', self.id)],
            'context': {
                'default_res_model': 'helpdesk.ticket',
                'default_res_id': self.id,
            }
        }

    def _get_age_str(self):
        """Return a human-readable age based on create_date."""
        self.ensure_one()
        if not self.create_date:
            return ''
        now = fields.Datetime.now()
        delta = now - fields.Datetime.from_string(self.create_date)
        days = delta.days
        seconds = delta.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        parts = []
        if days:
            parts.append(_('%s d') % days)
        if hours:
            parts.append(_('%s h') % hours)
        if minutes and not days:
            parts.append(_('%s m') % minutes)
        return ' '.join(parts) or _('0 m')

    def _get_all_field_names_for_csv(self):
        # Exclude 2many technical fields to keep CSV simple
        field_names = []
        for name, field in self._fields.items():
            if field.type in ('one2many', 'many2many'):
                continue
            field_names.append(name)
        # Keep a deterministic order with some useful fields first
        preferred = ['id', 'name', 'partner_id', 'assignee_id', 'priority', 'stage', 'channel', 'sla_deadline', 'closed_date', 'create_date']
        ordered = preferred + [n for n in field_names if n not in preferred]
        return ordered

    def action_export_csv(self):
        self.check_access_rights('read')
        # Only managers should be able to trigger via server action; also enforce by group
        if not self.env.user.has_group('helpdesk_lite.group_helpdesk_manager'):
            raise AccessError(_('Only Helpdesk Managers can export CSV.'))
        # Determine records to export; if none selected, export all
        records = self
        if not records:
            records = self.search([])
        field_names = self._get_all_field_names_for_csv()
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(field_names)
        for rec in records.sudo():
            row = []
            for name in field_names:
                val = rec[name]
                # serialize values
                if isinstance(val, models.BaseModel):
                    # Many2one -> display_name/id
                    if val and val.exists():
                        row.append('%s' % (val.display_name))
                    else:
                        row.append('')
                elif isinstance(val, (datetime,)):
                    row.append(fields.Datetime.to_string(val))
                else:
                    row.append(val if val is not False else '')
            writer.writerow(row)
        data = buf.getvalue().encode('utf-8')
        attachment = self.env['ir.attachment'].create({
            'name': 'helpdesk_tickets.csv',
            'type': 'binary',
            'datas': base64.b64encode(data),
            'mimetype': 'text/csv',
            'res_model': 'helpdesk.ticket',
            'public': False,
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self',
        }

    # ---------------------------------------------------------------------
    # CRON
    # ---------------------------------------------------------------------
    @api.model
    def _cron_check_sla_overdue(self):
        now = fields.Datetime.now()
        domain = [('sla_deadline', '!=', False), ('sla_deadline', '<', now), ('stage', '!=', 'done')]
        overdue_tickets = self.search(domain)
        for t in overdue_tickets:
            # Post message to chatter
            t.message_post(body=_('SLA deadline is overdue as of %(now)s.', now=now))
            # Schedule activity for assignee
            if t.assignee_id:
                try:
                    t.activity_schedule(
                        act_type_xmlid='mail.mail_activity_data_warning',
                        date_deadline=fields.Date.today(),
                        summary=_('SLA overdue'),
                        note=_('Ticket %(name)s is overdue its SLA deadline (%(deadline)s).', name=t.name, deadline=t.sla_deadline)
                    )
                except Exception:
                    # ignore activity scheduling issues
                    pass
        return True
