from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    # Relación con la obra
    obra_id = fields.Many2one('project.project', string='Obra', readonly=True)

    total_facturado = fields.Float(
        string="Total Facturado",
        readonly=True
    )
    subtotal_facturado = fields.Float(
        string="Subtotal Facturado",
        readonly=True
    )
    diferencia_total = fields.Float(
        string="Diferencia Total",
        readonly=True
    )

    first_receipt_date = fields.Datetime('Fecha Primer Recibo', readonly=True)
    last_receipt_date = fields.Datetime('Fecha Último Recibo', readonly=True)
    delay_first_receipt = fields.Float(
        'Días (Confirmación → Primer Recibo)', 
        readonly=True, 
        group_operator='avg'
    )
    delay_last_receipt = fields.Float(
        'Días (Confirmación → Último Recibo)', 
        readonly=True, 
        group_operator='avg'
    )


    def _select(self):
        return super(PurchaseReport, self)._select() + """
            , po.x_studio_obra as obra_id
            , COALESCE(SUM(inv.total_facturado), 0) AS total_facturado
            , COALESCE(SUM(inv.subtotal_facturado), 0) AS subtotal_facturado
            , (SUM(l.price_total) - COALESCE(SUM(inv.total_facturado), 0)) AS diferencia_total
            , MAX(sp_first.date_done) AS first_receipt_date
            , MAX(sp_last.date_done) AS last_receipt_date
            , MAX(EXTRACT(EPOCH FROM (sp_first.date_done - po.date_planned)) / 86400) AS delay_first_receipt  
            , MAX(EXTRACT(EPOCH FROM (sp_last.date_done - po.date_planned)) / 86400) AS delay_last_receipt
            
        """

    def _from(self):
        return super(PurchaseReport, self)._from() + """
            LEFT JOIN project_project project ON po.x_studio_obra = project.id
            LEFT JOIN (
                SELECT
                    pol.id AS purchase_line_id,
                    SUM(aml.price_total) AS total_facturado,
                    SUM(aml.price_subtotal) AS subtotal_facturado
                FROM
                    purchase_order_line pol
                JOIN
                    account_move_line aml ON aml.purchase_line_id = pol.id
                JOIN
                    account_move am ON am.id = aml.move_id
                WHERE
                    am.state = 'posted'
                    AND am.move_type = 'in_invoice'
                GROUP BY
                    pol.id
            ) inv ON inv.purchase_line_id = l.id
            LEFT JOIN (
                SELECT 
                    po.id AS order_id,
                    MIN(sp.date_done) AS date_done 
                FROM stock_picking sp
                JOIN stock_move sm ON sm.picking_id = sp.id
                JOIN purchase_order_line pol ON pol.id = sm.purchase_line_id
                JOIN purchase_order po ON po.id = pol.order_id
                WHERE sp.state = 'done'
                GROUP BY po.id
            ) sp_first ON sp_first.order_id = po.id
            LEFT JOIN (
                SELECT 
                    po.id AS order_id,
                    MAX(sp.date_done) AS date_done 
                FROM stock_picking sp
                JOIN stock_move sm ON sm.picking_id = sp.id
                JOIN purchase_order_line pol ON pol.id = sm.purchase_line_id
                JOIN purchase_order po ON po.id = pol.order_id
                WHERE sp.state = 'done'
                GROUP BY po.id
            ) sp_last ON sp_last.order_id = po.id
        """

    def _group_by(self):
        return super(PurchaseReport, self)._group_by() + """
            , po.id
            , po.x_studio_obra
            , po.amount_total
            , l.price_total
        """
