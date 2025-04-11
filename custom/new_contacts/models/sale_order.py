from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    angariador_id = fields.Many2one('res.users', string='Angariador')

    def _prepare_invoice(self):
        """Adiciona o Angariador nos valores da fatura"""
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        if self.angariador_id:
            invoice_vals['angariador_id'] = self.angariador_id.id  # Passa o angariador para a fatura

        return invoice_vals

    # @api.model
    # def create(self, vals):
    #     """Se a venda for criada a partir de uma oportunidade (opportunity_id),
    #     copia o angariador da oportunidade (crm.lead) para a venda (sale.order)."""
    #     if vals.get('opportunity_id'):
    #         lead = self.env['crm.lead'].browse(vals['opportunity_id'])
    #         if lead.angariador_id:
    #             vals['angariador_id'] = lead.angariador_id.id  # Copia o angariador
    #     return super(SaleOrder, self).create(vals)
# (Console)
# >>> sale_orders = self.env['sale.order'].search([('opportunity_id','=',False)])
# >>> sale_orders
# sale.order(22, 21, 16, 14, 13, 12, 10, 8, 7, 6, 4, 3, 9, 15, 11, 17, 20, 19, 5, 2, 1, 18)


# Busca TODOS os registros de attendance (sem filtro)
# all_attendances = env['hr.attendance'].search([])
# print("Todos os registros:", all_attendances)
#
# # Verifica se algum tem check_out=False
# for att in all_attendances:
#     print(f"ID: {att.id}, Check-in: {att.check_in}, Check-out: {att.check_out}")

# country_names = [country.name for country in env['res.country'].search([])]
# print(country_names)
