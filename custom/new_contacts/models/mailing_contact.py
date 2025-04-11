from odoo import models, fields


class MailingContact(models.Model):
    _inherit = 'mailing.contact'

    phone = fields.Char()
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    street = fields.Char("Street")
    city = fields.Char("City")
    state_id = fields.Many2one('res.country.state', string="State")
    country_id = fields.Many2one('res.country', string="Country")
    postcode = fields.Char("Postal Code")
    image_1920 = fields.Image("Picture")

    def delete_all_list_contacts(self):
        # Busca a lista de contatos chamada "NOVOS CONTATOS 2025"
        mailing_list = self.env['mailing.list'].search([('name', '=', 'NOVOS CONTATOS 2025')], limit=1)

        if mailing_list:  # Verifica se a lista foi encontrada
            # Busca todos os contatos que estão associados à lista encontrada
            contacts = self.env['mailing.contact'].search([('list_ids', 'in', mailing_list.id)])

            if contacts:  # Verifica se existem contatos para deletar
                contacts.unlink()  # Remove todos os contatos encontrados
