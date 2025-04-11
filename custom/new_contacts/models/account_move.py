from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    angariador_id = fields.Many2one(
        'res.users',
        string='Angariador',
        store=True,
        # readonly=False,
        # states={'posted': [('readonly', True)]}
    )






    # @api.depends('invoice_line_ids.sale_line_ids.order_id.angariador_id')
    # def _compute_angariador(self):
    #     for move in self:
    #         # Pega todas as vendas relacionadas através das linhas
    #         sale_orders = move.invoice_line_ids.sale_line_ids.order_id
    #
    #         # Se houver vendas com angariador definido, pega o primeiro encontrado
    #         if sale_orders and sale_orders[0].angariador_id:
    #             move.angariador_id = sale_orders[0].angariador_id
    #         else:
    #             move.angariador_id = False