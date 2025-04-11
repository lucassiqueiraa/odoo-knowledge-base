from odoo import models, fields


class MaintenanceChecklistTemplate(models.Model):
    _name = 'maintenance.checklist.template'
    _description = 'Modelo de Checklist para Manutenção'

    name = fields.Char(required=True, string="Nome do Template")
    category_ids = fields.One2many(
        'maintenance.equipment.category',
        'checklist_template_id',
        string='Categorias que usam este template'
    )
    equipment_ids = fields.Many2many(
        'maintenance.equipment',
        'equipment_checklist_template_rel',
        'template_id',
        'equipment_id',
        string='Equipamentos Associados'
    )



    line_ids = fields.One2many(
        'maintenance.checklist.item',
        'template_id',
        string='Itens da Checklist'
    )




class MaintenanceChecklistItem(models.Model):
    _name = 'maintenance.checklist.item'
    _description = 'Item da Checklist'

    name = fields.Char(string='Nome do Item', required=True)
    template_id = fields.Many2one('maintenance.checklist.template', required=True)

# Essa classe tem haver com maintenance request para receber oque vem dos templates de checklist
class MaintenanceChecklistExecution(models.Model):
    _name = 'maintenance.checklist.execution'
    _description = 'Checklist de Execução de Manutenção'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Requisição de Manutenção', required=True, ondelete='cascade')
    item_description = fields.Char('Item')
    is_done = fields.Boolean('Feito')
