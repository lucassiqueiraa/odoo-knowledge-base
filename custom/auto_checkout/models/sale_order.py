from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def _onchange_partner_update_product_descriptions(self):
        """Ao alterar o cliente, verifica e atualiza a descrição dos produtos."""
        for order in self:
            for line in order.order_line:
                if not line.product_id:
                    continue  # Se não há produto, pula essa linha

                product = line.product_id.product_tmpl_id  # Pegamos o template do produto
                customer = order.partner_id  # Cliente do pedido

                # Busca se o cliente tem uma referência personalizada para esse produto
                custom_reference = product.customer_reference_ids.filtered(lambda ref: ref.partner_id == customer)

                if custom_reference:
                    custom_name = custom_reference[0].custom_name or line.product_id.display_name
                    custom_ref = custom_reference[0].custom_ref or ''
                    line.name = f"[{custom_ref}] {custom_name}" if custom_ref else custom_name
                else:
                    # Se o cliente não está na lista, usa a descrição padrão do produto
                    line.name = line.product_id.display_name

    # def _prepare_invoice(self):
    #     """
    #     Prepara o dicionário de valores para criar a fatura de um pedido de venda.
    #     Esse método pode ser sobrescrito para personalizar a criação da fatura.
    #     Apenas a descrição das linhas da fatura será modificada, mantendo os demais dados.
    #     """
    #     self.ensure_one()
    #
    #     # Prepara os dados da fatura (mantendo o que já estava lá)
    #     invoice_vals = super(SaleOrder, self)._prepare_invoice()
    #
    #     # Agora, ajustamos apenas a descrição das linhas de fatura
    #     for invoice_line in invoice_vals['invoice_line_ids']:
    #         # Busca a linha de pedido de venda correspondente à linha de fatura
    #         sale_order_line = self.order_line.filtered(lambda line: line.product_id.id == invoice_line['product_id'])
    #
    #         if sale_order_line:
    #             # Obtém a descrição personalizada (se houver) do pedido de venda
    #             custom_description = sale_order_line.name if sale_order_line.name else sale_order_line.product_id.name
    #
    #             # Atualiza a descrição da linha de fatura com a descrição personalizada
    #             invoice_line['name'] = custom_description
    #
    #     return invoice_vals


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id')
    def _onchange_product_id_set_custom_description(self):
        """Ao selecionar um produto, verifica se o cliente da venda está na lista de clientes habituais do produto."""
        for line in self:
            if not line.product_id or not line.order_id.partner_id:
                continue

            customer = line.order_id.partner_id
            product = line.product_id.product_tmpl_id  # Pegamos o template do produto

            # Busca se o cliente tem uma referência personalizada para esse produto
            custom_reference = product.customer_reference_ids.filtered(lambda ref: ref.partner_id == customer)

            if custom_reference:
                custom_name = custom_reference[0].custom_name or line.product_id.display_name
                custom_ref = custom_reference[0].custom_ref or ''

                # Atualiza a descrição do produto na linha de venda
                line.name = f"[{custom_ref}] {custom_name}" if custom_ref else custom_name
