# -*- coding: utf-8 -*-
from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class HelpdeskPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'helpdesk_count' in counters:
            partner = request.env.user.partner_id
            count = request.env['helpdesk.ticket'].sudo().search_count([('partner_id', '=', partner.id)])
            values['helpdesk_count'] = count
        return values

    @http.route(['/my/helpdesk', '/my/helpdesk/page/<int:page>'], type='http', auth='user', website=True)
    def portal_my_helpdesk(self, page=1, sortby='date', stage=None, priority=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        Helpdesk = request.env['helpdesk.ticket'].sudo()
        domain = [('partner_id', '=', partner.id)]
        if stage:
            domain.append(('stage', '=', stage))
        if priority:
            domain.append(('priority', '=', priority))

        # sorting
        sort_options = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Title'), 'order': 'name asc'},
            'priority': {'label': _('Priority'), 'order': 'priority desc, create_date desc'},
        }
        order = sort_options.get(sortby, sort_options['date'])['order']

        tickets_count = Helpdesk.search_count(domain)
        pager = portal_pager(url='/my/helpdesk', total=tickets_count, page=page, step=20, url_args={'sortby': sortby, 'stage': stage or '', 'priority': priority or ''})
        tickets = Helpdesk.search(domain, limit=20, offset=pager['offset'], order=order)

        values.update({
            'tickets': tickets,
            'page_name': 'helpdesk',
            'pager': pager,
            'default_url': '/my/helpdesk',
            'sortby': sortby,
            'sort_options': sort_options,
            'selected_stage': stage,
            'selected_priority': priority,
        })
        return request.render('helpdesk_lite.portal_my_helpdesk', values)

    @http.route(['/my/helpdesk/<int:ticket_id>'], type='http', auth='user', website=True)
    def portal_helpdesk_ticket(self, ticket_id, **kw):
        partner = request.env.user.partner_id
        ticket = request.env['helpdesk.ticket'].sudo().browse(ticket_id)
        if not ticket.exists() or ticket.partner_id.id != partner.id:
            return request.redirect('/my')
        return request.render('helpdesk_lite.portal_helpdesk_ticket', {'ticket': ticket})

    @http.route(['/my/helpdesk/create'], type='http', auth='user', website=True, methods=['GET', 'POST'])
    def portal_create_helpdesk(self, **post):
        partner = request.env.user.partner_id
        if request.httprequest.method == 'POST':
            name = (post.get('name') or '').strip()
            description = (post.get('description') or '').strip()
            if len(name) <= 3:
                values = {'error': _('Title must be longer than 3 characters.'), 'post': post}
                return request.render('helpdesk_lite.portal_helpdesk_create', values)
            vals = {
                'name': name,
                'description': description,
                'partner_id': partner.id,
                'channel': 'portal',
            }
            ticket = request.env['helpdesk.ticket'].sudo().create(vals)
            return request.redirect('/my/helpdesk/%s' % ticket.id)
        return request.render('helpdesk_lite.portal_helpdesk_create', {})
