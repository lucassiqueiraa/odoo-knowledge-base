from odoo import models, fields


class MaintenanceMaterialTemplate(models.Model):
    _name = 'maintenance.material.template'
    _description = 'Template de Materiais para Manutenção'

    name = fields.Char(required=True, string="Nome do Template")

    category_ids = fields.One2many(
        'maintenance.equipment.category',
        'material_template_id',
        string='Categorias que usam este template'
    )
    equipment_ids = fields.Many2many(
        'maintenance.equipment',
        'equipment_material_template_rel',
        'template_id',
        'equipment_id',
        string='Equipamento Específico'
    )

    line_ids = fields.One2many(
        'maintenance.material.template.line',
        'template_id',
        string='Materiais do Template'
    )

    hygiene_checklist_ids = fields.One2many(
        'maintenance.material.hygiene.item',
        'material_template_id',
        string='Checklist de Higienização'
    )


class MaintenanceMaterialTemplateLine(models.Model):
    _name = 'maintenance.material.template.line'
    _description = 'Produto no Template de Materiais'

    template_id = fields.Many2one('maintenance.material.template', string="Template", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produto', required=True)
    quantity = fields.Float(string='Quantidade', default=1.0)


class MaintenanceMaterialHygieneItem(models.Model):
    _name = 'maintenance.material.hygiene.item'

    _description = 'Item da Checklist de Higienização'
    _order = 'sequence, id'

    name = fields.Char(string='Item', required=True)
    material_template_id = fields.Many2one(
        'maintenance.material.template',
        string='Template de Material',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequência', default=10)
    notes = fields.Text(string='Instruções/Observações')


class MaintenanceHygieneExecution(models.Model):
    _name = 'maintenance.hygiene.execution'
    _description = 'Execução de Checklist de Higienização'

    maintenance_request_id = fields.Many2one(
        'maintenance.request',
        string='Requisição de Manutenção',
        required=True,
        ondelete='cascade'
    )
    item_id = fields.Many2one(
        'maintenance.material.hygiene.item',
        string='Item da Checklist'
    )
    item_description = fields.Char(string='Descrição',  store=True)
    is_done = fields.Boolean(string='Concluído', default=False)
    notes = fields.Text(string='Observações')