from odoo import models, fields, api
from datetime import timedelta, datetime

class MaintenancePlan(models.Model):
    _name = 'maintenance.plan'
    _description = 'Plano de Manutenção Preventiva'

    name = fields.Char(string='Nome do Plano', required=True)
    equipment_id = fields.Many2one('maintenance.equipment', string='Equipamento', required=True)
    technician_id = fields.Many2one('res.users', string='Técnico Responsável')
    frequency_days = fields.Integer(string='Frequência (dias)', required=True)
    next_maintenance_date = fields.Date(string='Próxima Manutenção', default=fields.Date.context_today)
    active = fields.Boolean(default=True)

    # TODO: AO CRIAR UMA MANUTENCAO COM UM EQUIPAMENTO QUE TEM UM TEMPLATE DE CHECKLIST ASSOCIADO ELE NAO PREENCHE A CHECKLIST PQ SO PREENCHE COM ONCHANGE

    @api.model
    def generate_maintenance_events(self):
        today = fields.Date.today()
        projection_limit = today + timedelta(days=30)  # cria eventos para os próximos 30 dias

        plans = self.search([('active', '=', True)])

        for plan in plans:
            date = plan.next_maintenance_date


            while date <= projection_limit:
                start_dt = datetime.combine(date, datetime.min.time()).replace(hour=9)
                stop_dt = start_dt + timedelta(hours=2)
                partner_id = plan.technician_id.partner_id.id if plan.technician_id else False

                # Verifica se já existe evento no calendário pra esse dia
                existing_event = self.env['calendar.event'].search([
                    ('start', '=', start_dt),
                    ('name', '=', f"Manutenção: {plan.equipment_id.name}")
                ], limit=1)

                if not existing_event:
                    self.env['calendar.event'].create({
                        'name'       : f"Manutenção: {plan.equipment_id.name}",
                        'start'      : start_dt,
                        'stop'       : stop_dt,
                        'user_id'    : plan.technician_id.id,
                        'allday'     : False,
                        'description': f"Manutenção preventiva para o equipamento {plan.equipment_id.name}.",
                        'partner_ids': [(4, partner_id)] if partner_id else [],
                    })

                # Se a data é hoje → cria também a manutenção
                if date == today:
                    existing_request = self.env['maintenance.request'].search([
                        ('equipment_id', '=', plan.equipment_id.id),
                        ('request_date', '=', today),
                        ('maintenance_type', '=', 'preventive')
                    ], limit=1)

                    print(plan.technician_id.name)
                    if not existing_request:
                        self.env['maintenance.request'].create({
                            'name'            : f"Manutenção Preventiva - {plan.equipment_id.name}",
                            'equipment_id'    : plan.equipment_id.id,
                            'request_date'    : today,
                            'user_id'         : plan.technician_id.id,
                            'maintenance_type': 'preventive',
                        })



                        # Atualiza próxima data de manutenção
                        plan.next_maintenance_date = date + timedelta(days=plan.frequency_days)

                # Avança para próxima data
                date += timedelta(days=plan.frequency_days)

