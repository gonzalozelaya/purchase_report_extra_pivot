from odoo import models, fields, tools

class PurchaseOrderReport(models.Model):
    _name = "purchase.order.report"
    _description = "Reporte de Órdenes de Compra"
    _auto = False
    _rec_name = 'user_id'

    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra', readonly=True)
    name = fields.Char(string='Referencia', readonly=True)
    user_id = fields.Many2one('res.users', string='Responsable', readonly=True)
    order_count = fields.Integer("Cantidad de Órdenes", readonly=True)
    order_total = fields.Monetary(string='Total Orden', readonly=True)
    invoice_total = fields.Monetary(string='Total Facturado', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', readonly=True)
    obra_id = fields.Many2one('project.project', string='Obra', readonly=True)
    supplier_id = fields.Many2one('res.partner', string='Proveedor', readonly=True)

    # Fechas Para calculos entre la orden de compra con la fecha del primer y ultimo remito
    first_picking_date = fields.Datetime(string='Fecha Primer Remito', readonly=True)
    last_picking_date = fields.Datetime(string='Fecha Último Remito', readonly=True)
    date_planned = fields.Datetime(string='Fecha de Entrega Esperada', readonly=True)

    first_picking_days = fields.Float(string='Días Primer Remito', readonly=True, digits=(12, 2),group_operator='avg')
    last_picking_days = fields.Float(string='Días Último Remito', readonly=True, digits=(12, 2),group_operator='avg')

    # Fechas Para calculos entre la confirmación del requerimiento de compra con la fecha de creación de la orden de compra
    # la fecha de confirmación de la orden de compra
    requisition_date_end =fields.Datetime(string="Fecha de Confirmación del requisito", readonly=True)
    order_create_date =fields.Datetime(string="Fecha de Confirmación del requisito", readonly=True)
    order_confirmation_date =fields.Datetime(string="Fecha de Confirmación del requisito", readonly=True)

    avg_days_requisition_to_order = fields.Float(string='Días Confirmación Requerimiento y Creación OP', readonly=True, digits=(12, 2),group_operator='avg')
    avg_days_requisition_to_confirmation = fields.Float(string='Días Confirmación Requerimiento y Confirmación OP', readonly=True, digits=(12, 2),group_operator='avg')

    def _select(self):
        return """
            SELECT
                MIN(po.id) AS id,
                MIN(po.id) AS purchase_order_id,
                po.x_studio_responsable_de_compraspc AS user_id,
                po.x_studio_obra AS obra_id,
                COUNT(DISTINCT po.id) AS order_count,
                MIN(po.name) AS name,
                po.currency_id AS currency_id,
                po.amount_total AS order_total,
                COALESCE(SUM(am.amount_total), 0) AS invoice_total,
                po.partner_id AS supplier_id,
                MIN(po.date_planned) AS date_planned,
                
                -- Usamos subconsultas para evitar la duplicación de registros
                -- Fechas de Stock Picking
                (SELECT MIN(sp.date_done) 
                 FROM stock_picking sp 
                 WHERE sp.origin = po.name 
                   AND sp.state = 'done') AS first_picking_date,
                (SELECT MAX(sp.date_done) 
                 FROM stock_picking sp 
                 WHERE sp.origin = po.name 
                   AND sp.state = 'done') AS last_picking_date,
                
                
                -- Cálculo de días entre la entrega esperada y los stock picking
                CEIL((SELECT EXTRACT(EPOCH FROM (po.date_planned - MIN(sp.date_done)))/86400
                      FROM stock_picking sp
                      WHERE sp.origin = po.name
                        AND sp.state = 'done')) AS first_picking_days,
                CEIL((SELECT EXTRACT(EPOCH FROM (po.date_planned - MAX(sp.date_done)))/86400
                      FROM stock_picking sp
                      WHERE sp.origin = po.name
                        AND sp.state = 'done')) AS last_picking_days,


                -- Fechas de Requerimiento y Orden de Compra
                req.date_end AS requisition_date_end,
                po.create_date AS order_create_date,
                po.x_studio_fecha_confirmacin AS order_confirmation_date,
    
                -- Promedio de días entre (date_end de requisition y create_date de purchase.order)
                CEIL(EXTRACT(EPOCH FROM (po.create_date - req.date_end)) / 86400) AS avg_days_requisition_to_order,
    
                -- Promedio de días entre (date_end de requisition y x_studio_fecha_confirmacin de purchase.order)
                CEIL(EXTRACT(EPOCH FROM (po.x_studio_fecha_confirmacin - req.date_end)) / 86400) AS avg_days_requisition_to_confirmation
                
                
        """
        
        
    def _from(self):
        return """
            FROM purchase_order po
            LEFT JOIN account_move am 
                ON am.invoice_origin = po.name
                AND am.move_type IN ('in_invoice', 'in_refund')
                AND am.state = 'posted'
            LEFT JOIN purchase_requisition req 
                ON po.requisition_id = req.id
        """

    def _group_by(self):
        return """
            GROUP BY
                po.id,
                po.x_studio_responsable_de_compraspc,
                po.x_studio_obra,
                po.currency_id,
                po.partner_id,
                req.date_end
        """

    
    

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._select()}
                {self._from()}
                {self._group_by()}
            )
        """
        self.env.cr.execute(query)

    def action_open_purchase_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Órdenes de Compra',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.user_id.id)],
            'target': 'current',
        }




