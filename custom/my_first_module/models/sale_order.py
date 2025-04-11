from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"
    client_purchase_code = fields.Char()
    client_purchase_code2 = fields.Char()

# Automaticamente só com isso ela já adiciona os campos aos modelos?