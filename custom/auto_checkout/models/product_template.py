from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_reference_ids = fields.One2many(
        'product.customer.reference', 'product_tmpl_id', string="Clientes Habituais"
    )

    country_ids = fields.Many2many(
        'res.country',
        string="Países Vendidos (Template)"
    )

    all_variant_country_ids = fields.Many2many(
        'res.country',
        string="Todos os Países das Variantes",
        compute='_compute_all_variant_countries',
        inverse='_inverse_all_variant_country_ids',
        store=False
    )

    @api.depends('country_ids', 'product_variant_ids.variant_country_ids')
    def _compute_all_variant_countries(self):
        for template in self:
            variant_countries = self.env['res.country']
            for variant in template.product_variant_ids:
                variant_countries |= variant.variant_country_ids
            template.all_variant_country_ids = variant_countries | template.country_ids

    def _inverse_all_variant_country_ids(self):
        for template in self:
            # Obtemos todos os países vindos das variantes
            variant_countries = self.env['res.country']
            for variant in template.product_variant_ids:
                variant_countries |= variant.variant_country_ids

            # Países que o usuário deixou no campo (depois de editar)
            selected_countries = template.all_variant_country_ids

            # Os países adicionados diretamente no template devem ser:
            # tudo que está no campo agora, exceto o que veio das variantes
            new_template_countries = selected_countries - variant_countries

            # Atualiza os países diretamente do template
            template.country_ids = [(6, 0, new_template_countries.ids)]

            # Agora, vamos cuidar das variantes
            # Precisamos remover das variantes os países que foram tirados no template
            for variant in template.product_variant_ids:

                # Quais países essa variante tem hoje (campo total)
                current = variant.country_ids

                # No lugar do real_to_remove, usar:
                real_to_remove = current & (variant.country_ids - selected_countries)

                # E fazer:
                variant.variant_country_ids = [(3, cid) for cid in real_to_remove.ids]
                variant.country_ids = [(3, cid) for cid in real_to_remove.ids]

                if real_to_remove:
                    variant.country_ids = [(3, cid) for cid in real_to_remove.ids]


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Campo manual por variante
    variant_country_ids = fields.Many2many(
        'res.country',
        string="Países Específicos da Variante"
    )

    country_ids = fields.Many2many(
        'res.country',
        string="Países (Template + Variante)",
        compute='_compute_total_countries',
        inverse='_inverse_total_countries',
        store=False
    )

    @api.depends('variant_country_ids', 'product_tmpl_id.country_ids')
    def _compute_total_countries(self):
        for variant in self:
            variant.country_ids = variant.variant_country_ids | variant.product_tmpl_id.country_ids

    def _inverse_total_countries(self):
        for variant in self:
            # Adiciona apenas os países que não vieram do template
            new_countries = self.env['res.country']
            for record in variant.country_ids:
                if record not in variant.product_tmpl_id.country_ids:
                    new_countries += record
            variant.variant_country_ids = new_countries
