from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    # Campo relacionado, busca o modelo do equipamento selecionado
    equipment_model = fields.Char(string="Modelo do equipamento", related='equipment_id.model', store=True)

    timesheet_ids = fields.One2many(
        'maintenance.timesheet',
        'maintenance_id',
        string='Registro de Horas'
    )
    total_hours_spent = fields.Float(
        string='Total de Horas',
        compute='_compute_total_hours',
        store=True,
        help='Total de horas gastas nesta manutenção'
    )

    checklist_execution_ids = fields.One2many(
        'maintenance.checklist.execution',
        'maintenance_request_id',
        string='Checklist',
        copy=False
    )

    checklist_hygiene_execution_ids = fields.One2many(
        'maintenance.hygiene.execution',
        'maintenance_request_id',
        string='Checklist',
        copy=False,
    )

    can_edit_prevention_checklist = fields.Boolean(
        string='Pode Editar Checklist de Prevenção',
        compute='_compute_can_edit_prevention_checklist',
    )

    # Campo computado para controlar a edição
    can_edit_hygiene_checklist = fields.Boolean(
        string='Pode Editar Checklist de Higiene',
        compute='_compute_can_edit_hygiene_checklist',
        store=False  # Não armazenar, pois depende do estágio atual
    )

    @api.depends('stage_id')
    def _compute_can_edit_hygiene_checklist(self):
        for record in self:
            # Substitua pelo ID ou código correto do estágio "In Progress"
            in_progress_stage = self.env.ref('maintenance.stage_1')
            record.can_edit_hygiene_checklist = record.stage_id.id == in_progress_stage.id

    @api.depends('stage_id')
    def _compute_can_edit_prevention_checklist(self):
        for record in self:
            repaired_stage = self.env.ref('maintenance.stage_3')
            record.can_edit_prevention_checklist = record.stage_id.id == repaired_stage.id

    material_line_ids = fields.One2many('maintenance.material.line', 'maintenance_id', string='Materiais Usados')
    consumo_realizado = fields.Boolean(string="Consumo Lançado", default=False)

    def action_view_details(self):
        self.ensure_one()
        return {
            'name'     : self.name,
            'type'     : 'ir.actions.act_window',
            'res_model': 'maintenance.request',
            'res_id'   : self.id,
            'view_mode': 'form',
            'target'   : 'current',
        }

    @api.onchange('equipment_id')
    def onchange_equipment_id(self):
        """Atualiza checklists e materiais quando o equipamento muda"""
        self._clear_checklists_and_materials()

        # Obtém os templates
        checklist_templates = self._get_checklist_templates()
        material_templates = self._get_material_templates()

        # Processa checklists e materiais
        self._process_preventive_checklists(checklist_templates)
        self._process_materials(material_templates)
        self._process_hygiene_checklists(material_templates)

    def _clear_checklists_and_materials(self):
        """Limpa todos os checklists e materiais"""
        self.write({
            'checklist_execution_ids'        : [(5, 0, 0)],
            'material_line_ids'              : [(5, 0, 0)],
            'checklist_hygiene_execution_ids': [(5, 0, 0)]
        })

    def _get_checklist_templates(self):
        """Obtém templates de checklist do equipamento e categoria"""
        templates = []
        if self.equipment_id.category_id.checklist_template_id:
            templates.append(self.equipment_id.category_id.checklist_template_id)
        if self.equipment_id.checklist_template_ids:
            templates.extend(self.equipment_id.checklist_template_ids)
        return templates

    def _get_material_templates(self):
        """Obtém templates de materiais do equipamento e categoria"""
        templates = []
        if self.equipment_id.category_id.material_template_id:
            templates.append(self.equipment_id.category_id.material_template_id)
        if self.equipment_id.material_template_ids:
            templates.extend(self.equipment_id.material_template_ids)
        return templates

    def _process_preventive_checklists(self, templates):
        """Processa checklists preventivos"""
        checklist_vals = []
        for template in templates:
            for item in template.line_ids:
                checklist_vals.append((0, 0, {
                    'item_description': item.name,
                    'is_done'         : False
                }))
        self.checklist_execution_ids = checklist_vals

    def _process_materials(self, templates):
        """Processa materiais"""
        material_vals = []
        for template in templates:
            for line in template.line_ids:
                material_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'quantity'  : line.quantity
                }))
        self.material_line_ids = material_vals

    def _process_hygiene_checklists(self, templates):
        """Processa checklists de higienização"""
        hygiene_vals = []
        for template in templates:
            for line in template.hygiene_checklist_ids:
                hygiene_vals.append((0, 0, {
                    'item_description': line.name,
                    'notes'           : line.notes,
                    'is_done': False,
                }))
        self.checklist_hygiene_execution_ids = hygiene_vals

    def write(self, vals):
        result = super(MaintenanceRequest, self).write(vals)
        # Auto-consumir materiais ao mudar para o estado reparado
        if vals.get('stage_id'):
            stage = self.env['maintenance.stage'].browse(vals['stage_id'])
            if stage.done and not self.consumo_realizado and self.material_line_ids:
                self.action_lancar_consumo()
        return result

    def action_lancar_consumo(self):
        StockPicking = self.env['stock.picking']
        StockMove = self.env['stock.move']

        # Obter o tipo de picking adequado para transferências internas
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id.company_id', '=', self.company_id.id)
        ], limit=1)

        if not picking_type:
            raise UserError('Tipo de operação para transferência interna não encontrado.')

        for request in self:
            if not request.material_line_ids or request.consumo_realizado:
                continue

            # Obter localizações de estoque de forma mais segura (busca em vez de ref)
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.company_id.id)], limit=1)
            if not warehouse:
                raise UserError('Armazém não encontrado para esta empresa.')

            # Origem: Estoque principal
            location_id = warehouse.lot_stock_id
            # Destino: Localização virtual para consumo
            location_dest_id = self.env['stock.location'].search([
                ('usage', '=', 'production'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)

            if not location_dest_id:
                # Fallback para localização de clientes se produção não existir
                location_dest_id = self.env['stock.location'].search([
                    ('usage', '=', 'customer'),
                    ('company_id', '=', self.company_id.id)
                ], limit=1)

            if not location_id or not location_dest_id:
                raise UserError('Não foi possível encontrar as localizações de estoque necessárias.')

            # Criar picking
            picking_vals = {
                'location_id'     : location_id.id,
                'location_dest_id': location_dest_id.id,
                'picking_type_id' : picking_type.id,
                'origin'          : f'Manutenção: {request.name}',
                'scheduled_date'  : fields.Datetime.now(),
                'move_type'       : 'direct',
            }

            picking = StockPicking.create(picking_vals)

            # Criar movimentações de estoque para cada linha de material
            moves_created = False
            for line in request.material_line_ids:
                if line.quantity <= 0:
                    continue

                move_vals = {
                    'name'            : f"Consumo: {line.product_id.name} - Manutenção {request.name}",
                    'product_id'      : line.product_id.id,
                    'product_uom_qty' : line.quantity,
                    'product_uom'     : line.product_id.uom_id.id,
                    'picking_id'      : picking.id,
                    'location_id'     : location_id.id,
                    'location_dest_id': location_dest_id.id,
                }
                StockMove.create(move_vals)
                moves_created = True

            if not moves_created:
                picking.unlink()
                continue

            # Confirmar e validar o picking
            picking.action_confirm()
            picking.action_assign()

            # Lidar com disponibilidade parcial
            # Pelo código que permite disponibilidade parcial:
            for move in picking.move_ids_without_package:
                if move.state == 'assigned':
                    # Quantidade total disponível
                    move.quantity_done = move.product_uom_qty
                else:
                    # Quantidade parcial - use a quantidade reservada
                    move.quantity_done = move.reserved_availability
                    # Ou defina como zero se preferir
                    # move.quantity_done = 0

            # Adicione uma mensagem informativa sobre produtos com disponibilidade parcial
            produtos_sem_estoque = [move.product_id.name for move in picking.move_ids_without_package if
                                    move.state != 'assigned']
            if produtos_sem_estoque:
                mensagem = "Alguns produtos têm disponibilidade parcial: " + ", ".join(produtos_sem_estoque)
                # Use logger para registrar a mensagem ou mostre em uma notificação
                _logger.info(mensagem)

            picking.button_validate()
            request.consumo_realizado = True

            return {
                'type'  : 'ir.actions.client',
                'tag'   : 'display_notification',
                'params': {
                    'title'  : 'Sucesso!',
                    'message': 'Consumo de materiais registrado com sucesso.',
                    'sticky' : False,
                }
            }

    @api.depends('timesheet_ids.hours')
    def _compute_total_hours(self):
        for request in self:
            request.total_hours_spent = sum(request.timesheet_ids.mapped('hours'))

    def action_open_timesheets(self):
        self.ensure_one()
        action = {
            'name'     : 'Horas Trabalhadas',
            'type'     : 'ir.actions.act_window',
            'res_model': 'maintenance.timesheet',
            'view_mode': 'tree,form',
            'domain'   : [('maintenance_id', '=', self.id)],
            'context'  : {
                'default_maintenance_id': self.id,
                'default_date'          : fields.Date.context_today(self),
            }
        }
        if self.user_id:
            employee = self.env['hr.employee'].search([('user_id', '=', self.user_id.id)], limit=1)
            if employee:
                action['context']['default_employee_id'] = employee.id

        return action


class MaintenanceTimesheet(models.Model):
    _name = 'maintenance.timesheet'
    _description = 'Registro de Horas em Manutenção'
    _order = 'date desc, id desc'

    maintenance_id = fields.Many2one('maintenance.request', string='Manutenção', required=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Funcionário', required=True)
    user_id = fields.Many2one('res.users', string='Usuário', related='employee_id.user_id', store=True)
    date = fields.Date(string='Data', required=True, default=fields.Date.context_today)
    hours = fields.Float(string='Horas Trabalhadas', required=True)
    description = fields.Text(string='Descrição do Trabalho')

    @api.onchange('maintenance_id')
    def _onchange_maintenance_id(self):
        if self.maintenance_id and self.maintenance_id.user_id:
            employee = self.env['hr.employee'].search([('user_id', '=', self.maintenance_id.user_id.id)], limit=1)
            if employee:
                self.employee_id = employee.id
