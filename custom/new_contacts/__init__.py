from . import models
from . import wizard


# from odoo import api, SUPERUSER_ID
#
# def _post_init_hook(cr, registry):
#     """Cria automaticamente a lista de contatos 'NOVOS CONTATOS 2023' se ainda não existir."""
#     env = api.Environment(cr, SUPERUSER_ID, {})
#     if not env['mailing.list'].search([('name', '=', 'NOVOS CONTATOS 2023')], limit=1):
#         env['mailing.list'].create({
#             'name': 'NOVOS CONTATOS 2023',
#             'is_public': True,  # Define se a lista pode ser usada publicamente
#         })
