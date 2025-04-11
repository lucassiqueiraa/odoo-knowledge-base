from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.onchange('partner_id')
    def _onchange_partner_update_product_descriptions(self):
        """Ao alterar o cliente, verifica e atualiza a descrição dos produtos."""
        for invoice in self:
            for line in invoice.invoice_line_ids:
                if not line.product_id:
                    continue  # Se não há produto, pula essa linha

                product = line.product_id.product_tmpl_id  # Pegamos o template do produto
                customer = invoice.partner_id  # Cliente do pedido

                # Busca se o cliente tem uma referência personalizada para esse produto
                custom_reference = product.customer_reference_ids.filtered(lambda ref: ref.partner_id == customer)

                if custom_reference:
                    custom_name = custom_reference[0].custom_name or line.product_id.display_name
                    custom_ref = custom_reference[0].custom_ref or ''
                    line.name = f"[{custom_ref}] {custom_name}" if custom_ref else custom_name
                else:
                    # Se o cliente não está na lista, usa a descrição padrão do produto
                    line.name = line.product_id.display_name



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.onchange('product_id')
    def _onchange_product_id_set_custom_description(self):
        """Ao selecionar um produto, verifica se o cliente da fatura está na lista de clientes habituais do produto."""
        for line in self:
            if not line.product_id or not line.partner_id:
                continue

            customer = line.partner_id
            product = line.product_id.product_tmpl_id  # Pegamos o template do produto

            # Busca se o cliente tem uma referência personalizada para esse produto
            custom_reference = product.customer_reference_ids.filtered(lambda ref: ref.partner_id == customer)

            if custom_reference:
                custom_name = custom_reference[0].custom_name or line.product_id.display_name
                custom_ref = custom_reference[0].custom_ref or ''

                # Atualiza a descrição do produto na linha de venda
                line.name = f"[{custom_ref}] {custom_name}" if custom_ref else custom_name
