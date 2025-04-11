from odoo import models, fields

class ProductCustomerReference(models.Model):
    _name = 'product.customer.reference'
    _description = 'Referência Personalizada de Clientes para Produtos'

    # Varios clientes referenciados pertencem a 1 unico produto
    #     ID da Referencia          Produto                 Clientes                  Nome Personalizado        Referencia do cliente
    #         1                   Camisa  Polo                João                      Camiseta Azul                  REF123

    product_tmpl_id = fields.Many2one('product.template', string="Produto", required=True)
    partner_id = fields.Many2one('res.partner', string="Cliente", required=True)
    custom_name = fields.Char(string="Nome do Cliente para o Produto")
    custom_ref = fields.Char(string="Referência do Cliente")
