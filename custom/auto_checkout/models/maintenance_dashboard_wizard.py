# Arquivo: maintenance_dashboard_wizard.py
from odoo import models, fields, api


class MaintenanceEquipmentHistoryWizard(models.TransientModel):
    _name = 'maintenance.equipment.history.wizard'
    _description = 'Wizard para Selecionar Equipamento'

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipamento', required=True)

    def action_view_history(self):
        self.ensure_one()
        return {
            'name'     : f'Histórico: {self.equipment_id.name}',
            'type'     : 'ir.actions.act_window',
            'res_model': 'maintenance.equipment',
            'res_id'   : self.equipment_id.id,
            'view_mode': 'form',
            'view_id'  : self.env.ref('auto_checkout.maintenance_equipment_history_view').id,
            'target'   : 'current',
        }