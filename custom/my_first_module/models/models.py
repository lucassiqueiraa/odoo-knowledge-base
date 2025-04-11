from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class Car(models.Model):
    _name = "car.car"
    _description = "Car"

    # ======================
    # 1. FIELD DEFINITIONS
    # ======================
    name = fields.Char(string="Name")
    horse_power = fields.Integer(string="Horse Power")
    door_number = fields.Integer(string="Doors Number")
    driver_id = fields.Many2one('res.partner', string="Driver")
    parking_id = fields.Many2one('parking.parking', string="Parking")
    feature_ids = fields.Many2many("car.feature", string="Features")
    status = fields.Selection([
        ('new', 'New'),
        ('used', 'Used'),
        ('sold', 'Sold')
    ], string="Status", default="new")
    car_sequence = fields.Char(string="Sequence")
    total_speed = fields.Integer(string="Total Speed", compute="_compute_total_speed")
    message = fields.Char(string="Message", compute="_compute_message")

    # ======================
    # 2. COMPUTE METHODS
    # ======================
    @api.depends('horse_power')
    def _compute_total_speed(self):
        for car in self:
            car.total_speed = car.horse_power * 50

    @api.depends('driver_id', 'driver_id.name')
    def _compute_message(self):
        for car in self:
            car.message = f"Hello {car.driver_id.name}" if car.driver_id else "No driver assigned"

    # ======================
    # 3. CRUD METHODS (OVERRIDES)
    # ======================
    @api.model
    def create(self, vals):
        """Gera sequência automática ao criar um carro"""
        vals['car_sequence'] = self.env['ir.sequence'].next_by_code('car.sequence')
        return super().create(vals)

    def write(self, vals):
        """Valida cavalos ao atualizar"""
        if vals.get('horse_power') == 10:
            raise ValidationError('Horse power must be greater than 10')
        return super().write(vals)

    def unlink(self):
        """Impede exclusão se cavalos = 5"""
        for car in self:
            if car.horse_power == 5:
                raise ValidationError('Cannot delete car with 5 HP!')
        return super().unlink()

    # ======================
    # 4. BUSINESS LOGIC METHODS
    # ======================
    def set_car_to_used(self):
        """Muda status para 'used'"""
        self.status = 'used'

    def set_car_to_sold(self):
        """Muda status para 'sold' e envia e-mail"""
        self.status = 'sold'
        if self.driver_id.email:
            template = self.env.ref('my_first_module.car_mail_template')
            template.send_mail(self.id, force_send=True)

    # ======================
    # 5. CRON/SCHEDULED METHODS
    # ======================
    from odoo import fields

    def mark_old_cars_as_used(self):
        """Marca carros não vendidos após 30 dias como 'used'"""
        limit_date = fields.Datetime.now() - timedelta(days=30)
        old_cars = self.search([
            ('status', '=', 'new'),
            ('create_date', '<', fields.Datetime.to_string(limit_date))
        ])
        old_cars.write({'status': 'used'})
        _logger.info(f"✅ {len(old_cars)} carros marcados como USADOS")

    def send_weekly_sold_cars_report(self):
        """Envia relatório de carros vendidos na semana"""
        start_date = fields.Datetime.now() - timedelta(days=7)
        sold_cars = self.search([
            ('status', '=', 'sold'),
            ('write_date', '>=', fields.Datetime.to_string(start_date))
        ])

        admin_email = self.env['res.users'].search([('groups_id.name', '=', 'Administrator')], limit=1).email

        if sold_cars and admin_email:
            body = f"""
            <h2>Relatório Semanal de Carros Vendidos</h2>
            <p>Total vendidos: {len(sold_cars)}</p>
            <ul>
                {"".join(f"<li>{car.name} (Motor: {car.horse_power}HP)</li>" for car in sold_cars)}
            </ul>
            """

            self.env['mail.mail'].create({
                'subject'  : f'Relatório de Carros Vendidos - {datetime.now().strftime("%d/%m/%Y")}',
                'body_html': body,
                'email_to' : admin_email
            }).send()

        return True

    def clean_driverless_cars(self):
        """Remove carros sem motorista há mais de 90 dias"""
        limit_date = fields.Datetime.now() - timedelta(days=90)
        abandoned_cars = self.search([
            ('driver_id', '=', False),
            ('write_date', '<', fields.Datetime.to_string(limit_date))
        ])
        abandoned_cars.unlink()
        _logger.info(f"🗑️ {len(abandoned_cars)} carros sem motorista removidos")


class Parking(models.Model):
    _name = "parking.parking"

    name = fields.Char(string="Name")
    car_ids = fields.One2many('car.car', 'parking_id', 'Cars')


class CarFeatures(models.Model):
    _name = "car.feature"

    name = fields.Char(String="Name")
