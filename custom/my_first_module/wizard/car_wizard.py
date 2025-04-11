from odoo import models, fields


class CarWizard(models.TransientModel):
    _name = 'car.wizard'
    _description = 'Car Wizard'
    horse_power_plus = fields.Integer('Horse Power')

    def add_horse_power(self):
        print("****** test from car wizard *******")
        print("---> card_id:", self.env.context.get('active_id'))
        print("--> Horse power:", self.horse_power_plus)

        self.env['car.car'].browse(self.env.context.get('active_id')).write({
            'horse_power':self.horse_power_plus
        })

        return {'type': 'ir.actions.act_window_close'}