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

class MaintenanceMaterialTemplateLine(models.Model):
    _name = 'maintenance.material.template.line'
    _description = 'Produto no Template de Materiais'

    template_id = fields.Many2one('maintenance.material.template', string="Template", required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produto', required=True)
    quantity = fields.Float(string='Quantidade', default=1.0)
