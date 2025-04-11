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
        'base',
        'sale_management',  # Define o módulo a ser usando, importamos para usar a classe sale_order.py
        'mail',
        'project',
        'mass_mailing',
        'crm',
        'account',


    ],
    'data'       : [
        # Ter cuidado com a ordem pq as vezes em uma view pode ter uma action que chama outra e ai pode #@%!procrlh
        'security/ir.model.access.csv',
        'views/import_contacts_wizard_views.xml',
        'views/mailing_contact_views.xml',
        'views/menu.xml',
        'views/lead_view.xml',
        'views/sale_order_view.xml',
        'views/invoices_form_view.xml'


        # 'wizards/import_contacts_wizard_views.xml',

    ],
    'installable': True,
    'application': True,
    'license'    : 'LGPL-3',

}
