# Arquivo: maintenance_material.py
from odoo import models, fields, api


class MaintenanceMaterialLine(models.Model):
    _name = 'maintenance.material.line'
    _description = 'Materiais Utilizados na Manutenção'

    maintenance_id = fields.Many2one('maintenance.request', string='Manutenção', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Produto', required=True)
    quantity = fields.Float(string='Quantidade', default=1.0)
    unit_cost = fields.Float(string='Custo Unitário', related='product_id.standard_price', readonly=True)
    total_cost = fields.Float(string='Custo Total', compute='_compute_total_cost', store=True)

    @api.depends('quantity', 'unit_cost')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_cost