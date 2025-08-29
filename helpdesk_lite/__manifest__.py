# -*- coding: utf-8 -*-
{
    'name': 'Helpdesk Lite',
    'summary': 'Lightweight helpdesk/ticketing for Odoo Community',
    'version': '18.0.1.0.0',
    'category': 'Services/Helpdesk',
    'license': 'LGPL-3',
    'author': 'Roksana Piwowarczyk',
    'website': 'https://example.com/helpdesk_lite',
    'depends': ['base', 'mail', 'portal', 'contacts'],
    'data': [
        'security/helpdesk_security.xml',
        'security/ir.model.access.csv',
        'security/helpdesk_rules.xml',
        'views/helpdesk_menus.xml',
        'views/helpdesk_ticket_views.xml',
        'views/helpdesk_ticket_actions.xml',
        'report/helpdesk_ticket_report.xml',
        'report/helpdesk_ticket_report_actions.xml',
        'data/mail_template.xml',
        'data/cron.xml',
        'data/server_actions.xml',
        'portal/portal_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            # keep minimal; templates handle most
        ],
    },
    'application': True,
    'installable': True,
}