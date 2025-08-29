# -*- coding: utf-8 -*-
{
    'name': 'Company Asset Manager',
    'summary': 'Manage company assets and their service schedules with assignments and reporting',
    'version': '1.0.0',
    'license': 'LGPL-3',
    'author': 'Roksana Piwowarczyk',
    'category': 'Human Resources/Assets',
    'depends': ['base', 'mail', 'hr', 'contacts'],
    'data': [
        'security/asset_groups.xml',
        'security/ir.model.access.csv',
        'security/asset_record_rules.xml',
        'wizard/assign_wizard_views.xml',
        'views/asset_views.xml',
        'views/service_views.xml',
        'views/menus.xml',
        'data/server_actions.xml',
        'data/cron.xml',
    ],
    'application': True,
    'installable': True,
}
