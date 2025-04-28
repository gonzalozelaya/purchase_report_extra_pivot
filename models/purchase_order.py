from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    total_facturado = fields.Float(
        string="Total Facturado",
        readonly=True
    )

    
    def _select(self):
        return super()._select() + """,
            COALESCE((
                SELECT SUM(
                    CASE 
                        WHEN am.move_type = 'in_refund' THEN -am.amount_total 
                        ELSE am.amount_total 
                    END
                )
                FROM account_move am
                WHERE am.invoice_origin = po.name
                AND am.state = 'posted'
                AND am.move_type IN ('in_invoice', 'in_refund')
            ), 0) AS total_facturado
        """


    def _from(self):
        return super()._from()  # No se necesitan JOINS adicionales

    def _group_by(self):
        return super()._group_by() + ", po.name"  # Agrupación clave

    
    #def _from(self):
    #    return super(PurchaseReport, self)._from() + """
    #        LEFT JOIN (
    #            SELECT
    #                pol.id AS purchase_line_id,
    #                SUM(aml.price_total) AS total_facturado 
    #            FROM
    #                purchase_order_line pol
    #            JOIN
    #                account_move_line aml ON aml.purchase_line_id = pol.id
    #            JOIN
    #                account_move am ON am.id = aml.move_id
    #            WHERE
    #                am.state = 'posted'
    #                AND am.move_type IN ('in_invoice', 'in_refund')
    #            GROUP BY
    #                pol.id
    #        ) inv ON inv.purchase_line_id = l.id
    #        """

    #def _group_by(self):
    #    return super(PurchaseReport, self)._group_by()  # Eliminar adiciones innecesarias
    