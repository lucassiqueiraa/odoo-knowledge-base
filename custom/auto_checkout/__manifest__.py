{
    'name'       : 'new_contacts',
    'version'    : '16.0.0.0.1',
    'summary'    : 'new_contacts',
    'sequence'   : 10,
    'description': """
new_contacts
""",
    'category'   : 'Misc',
    'depends'    : [
        'hr_attendance',
        'resource',
        'product',
        'sale',
        'account',
        'product',
        'maintenance',
        'calendar',
        'stock',


    ],
    'data'       : [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/maintenance_request_form_inherit.xml',
        'views/maintenance_checklist_item_views.xml',
        'views/equipment_category_view_form.xml',
        'views/equipment_view_form.xml',
        'views/maintenance_plan_views.xml',
        'views/maintenance_kanbam.xml',
        'views/maintenance_timesheet.xml',
        'views/maintenance_material_template.xml',
        'views/maintenance_dashboard_views.xml',
        'views/maintenance_equipment_form.xml',
        'views/maintenance_dashboard_wizard_view.xml',
        'data/maintenance_plan_cron.xml',
        'data/cron.xml',

    ],
    'installable': True,
    'application': True,
    'license'    : 'LGPL-3',

}
