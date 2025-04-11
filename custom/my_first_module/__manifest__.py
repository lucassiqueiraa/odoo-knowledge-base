{
    'name'       : 'My First Module',
    'version'    : '16.0.0.0.1',
    'summary'    : 'My First Module',
    'sequence'   : 10,
    'description': """
My First Module
""",
    'category'   : 'Misc',
    'depends'    : [
        'base',
        'sale_management',  # Define o módulo a ser usando, importamos para usar a classe sale_order.py
        'mail',
        'fleet',
        'project',
    ],
    'data'       : [
        # Ter cuidado com a ordem pq as vezes em uma view pode ter uma action que chama outra e ai pode #@%!procrlh
        'views/security.xml',
        'security/group.xml',
        'security/rules.xml',
        'views/project_views.xml',
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
        'wizard/car_wizard.xml',
        'views/cars.xml',
        'views/parking.xml',
        'views/sequence.xml',
        'views/res_partner_inherit_form_view.xml',
        'data/car_template_mail.xml',
        'data/ir_cron.xml'

    ],
    'installable': True,
    'application': True,
    'license'    : 'LGPL-3',
}
