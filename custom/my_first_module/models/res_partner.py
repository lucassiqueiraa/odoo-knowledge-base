from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    message = fields.Char(String='Custom Message')
    other_information = fields.Char(String='Other Information')
    message_2 = fields.Char(String="Message 2")
    car_count = fields.Integer(String='Count', compute='get_car_number')

    def get_car_number(self):
        for rec in self:
            rec.car_count = self.env['fleet.vehicle'].search_count([('driver_id', '=', self.id)])

    def get_cars(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cars',
            'view_mode': 'tree',
            'res_model': 'fleet.vehicle',
            'domain': [('driver_id', '=', self.id)],
            'context': "{'create':False}"
        }