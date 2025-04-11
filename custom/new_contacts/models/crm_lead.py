from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    angariador_id = fields.Many2one(
        'res.users',
        string='Angariador',
        help="Pessoa que referenciou esta oportunidade"
    )

    def _prepare_opportunity_quotation_context(self):
        quotation_context = super(CrmLead, self)._prepare_opportunity_quotation_context()

        quotation_context.update({
            'default_angariador_id': self.angariador_id.id,
        })

        return quotation_context