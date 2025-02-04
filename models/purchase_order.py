
from odoo import models, api,fields
import logging

_logger = logging.getLogger(__name__)

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    obra = fields.Many2one(
        comodel_name='project.project',
        related='order_id.x_studio_obra',
        string='Obra',
        store=True,
        readonly=True
    )
    on_time_rate = fields.Float(string="A tiempo",
                                related="order_id.on_time_rate",
                                group_operator="max",
                                store=True,
                                readonly=True)


    def _select(self):
        select_str = super(PurchaseReport, self)._select()
        # Agrega la columna x_studio_obra
        select_str += """
        , po.on_time_rate/100 as on_time_rate
        , po.x_studio_obra as obra
        """
        
        return select_str

    def _group_by(self):
        group_by_str = super(PurchaseReport, self)._group_by()
        # Agrega x_studio_obra al GROUP BY
        group_by_str += """
        , po.x_studio_obra
        , po.on_time_rate
        """
        return group_by_str


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    on_time = fields.Boolean('A tiempo',
                            compute = '_compute_on_time',
                            store = True)

    on_time_rate = fields.Float(related='partner_id.on_time_rate', store = True,compute_sudo=False)


    @api.depends('date_planned','effective_date')
    def _compute_on_time(self):
        for record in self:
            if record.date_planned and record.effective_date:
                if record.date_planned < record.effective_date:
                    record.on_time = True
            record.on_time = False

    @api.model
    def update_existing_records(self):
        # Busca todos los registros existentes
        records = self.search([])
        # Llama al método compute para recalcular el valor
        records._compute_on_time()
        