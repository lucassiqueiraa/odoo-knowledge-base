import requests
from odoo import models, fields, api
from odoo.exceptions import UserError

class ImportContactsWizard(models.TransientModel):
    _name = 'import.contacts.wizard'
    _description = 'Wizard to Import Contacts from API'

    number_of_contacts = fields.Integer(string="Number of Contacts", default=1, required=True)

    def action_import_contacts(self):
        """ Import contacts from the API and associate them with the mailing list. """
        api_url = f"https://randomuser.me/api/?results={self.number_of_contacts}"

        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise UserError(f"Error fetching contacts: {e}")

        data = response.json().get('results', [])

        mailing_list = self.env['mailing.list'].search([('name', '=', 'NOVOS CONTATOS 2025')], limit=1)
        if not mailing_list:
            raise UserError("Mailing list 'NOVOS CONTATOS 2025' not found.")

        contact_model = self.env['mailing.contact']
        existing_emails = contact_model.search([]).mapped('email')

        for user in data:
            email = user.get('email')
            if email in existing_emails:
                continue  # Pula contato duplicado

            contact_model.create({
                'name': f"{user['name']['first']} {user['name']['last']}",
                'gender': user.get('gender'),
                'email': email,
                'phone': user.get('phone'),
                'street': user['location']['street']['name'],
                'city': user['location']['city'],
                'state_id': self.env['res.country.state'].search([('name', '=', user['location']['state'])], limit=1).id,
                'country_id': self.env['res.country'].search([('name', '=', user['location']['country'])], limit=1).id,
                'postcode': str(user['location']['postcode']),
                'image_1920': self._get_image_from_url(user['picture']['large']),
                'list_ids': [(4, mailing_list.id)],
            })

    def _get_image_from_url(self, url):
        """ Fetch image from URL and convert to base64. """
        try:
            import base64
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return base64.b64encode(response.content)
        except requests.RequestException:
            return False
