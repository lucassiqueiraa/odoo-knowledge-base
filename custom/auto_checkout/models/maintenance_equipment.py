from odoo import models, fields, api


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    # Campos que você já tem
    checklist_template_ids = fields.Many2many(
        'maintenance.checklist.template',
        'equipment_checklist_template_rel',
        'equipment_id',
        'template_id',
        string='Templates de Checklists Padrão do Equipamento'
    )

    material_template_ids = fields.Many2many(
        'maintenance.material.template',
        'equipment_material_template_rel',
        'equipment_id',
        'template_id',
        string='Template de Materiais Padrão do Equipamento'
    )

    # Os campos abaixo são computados para mostrar estatísticas no equipamento
    maintenance_count = fields.Integer(string='Contagem de Manutenções', compute='_compute_maintenance_stats')
    maintenance_hours = fields.Float(string='Horas de Manutenção', compute='_compute_maintenance_stats')
    maintenance_material_cost = fields.Monetary(string='Custo de Materiais', compute='_compute_maintenance_stats',
                                                currency_field='currency_id')

    # Campo para a moeda da empresa
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    @api.depends('maintenance_ids')
    def _compute_maintenance_stats(self):
        for equipment in self:
            maintenance_requests = self.env['maintenance.request'].search([
                ('equipment_id', '=', equipment.id),
                ('stage_id.done', '=', True)  # Apenas manutenções concluídas
            ])

            equipment.maintenance_count = len(maintenance_requests)
            equipment.maintenance_hours = sum(maintenance_requests.mapped('total_hours_spent'))

            # Calcular custo total dos materiais consumidos
            cost = 0
            for request in maintenance_requests:
                for line in request.material_line_ids:
                    cost += line.product_id.standard_price * line.quantity

            equipment.maintenance_material_cost = cost

    def action_view_maintenance_history(self):
        self.ensure_one()
        return {
            'name'     : f'Histórico de Manutenções: {self.name}',
            'type'     : 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'view_mode': 'tree,form',
            'domain'   : [('equipment_id', '=', self.id)],
            'context'  : {'default_equipment_id': self.id}
        }

class MaintenanceEquipmentCategory(models.Model):
    _inherit = 'maintenance.equipment.category'

    checklist_template_id = fields.Many2one(
        'maintenance.checklist.template',
        string='Template de Checklist',
        help="Template padrão para esta categoria"
    )

    material_template_id = fields.Many2one(
        'maintenance.material.template',
        string='Template de Materiais'
    )



