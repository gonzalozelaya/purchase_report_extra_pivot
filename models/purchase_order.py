
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
