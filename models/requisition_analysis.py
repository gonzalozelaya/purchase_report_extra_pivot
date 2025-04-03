from odoo import models, fields, api, tools

class RequisitionAnalysis(models.Model):
    _name = "requisition.analysis"
    _description = "Análisis de Requerimientos por Solicitante"
    _auto = False  # Indica que es una vista SQL
    _rec_name = 'requisition_id'  # Nombre por defecto del registro

    # Campos clave
    solicitante_id = fields.Many2one('res.users', string='Solicitante', readonly=True)
    requisition_count = fields.Integer("Cantidad de Requerimientos", readonly=True)
    requisition_id = fields.Many2one('purchase.requisition', string="Requerimiento", readonly=True)  # Enlace al requerimiento
    total_requisition = fields.Float("Total", readonly=True)  # Nuevo campo para el total
    po_count = fields.Integer("Cantidad de OC", readonly=True)
    additional_count = fields.Integer("Adicionales", readonly=True)
    delivery_days_avg = fields.Float(  # Cambiado a Float
        "Promedio Días (Pedido→Entrega)", 
        group_operator='avg',
        readonly=True,
        digits=(12, 0)  # Muestra como entero en la interfaz
    )


    def _select(self):
        return """
        SELECT
            pr.id AS id  -- ID único del análisis (requerido para la vista SQL)
            ,pr.user_id AS solicitante_id
            ,pr.id AS requisition_id  -- Enlace directo al requerimiento
            ,1 AS requisition_count  -- Cada fila representa 1 requerimiento
            ,(  -- Suma el total de las líneas del requerimiento
                SELECT SUM(pol.product_qty * pol.price_unit)
                FROM purchase_requisition_line pol
                WHERE pol.requisition_id = pr.id
            ) AS total_requisition
            ,(  -- Cantidad de OC asociadas
                SELECT COUNT(DISTINCT po.id)
                FROM purchase_order po
                WHERE po.requisition_id = pr.id
            ) AS po_count
            ,CASE 
                WHEN pr.x_studio_requerimiento_adicional IS NOT NULL THEN 1  -- Verifica si el Many2one tiene valor
                ELSE 0 
            END AS additional_count
            -- Nuevo cálculo de días promedio
            ,-- Cálculo correcto para fechas Date:
            COALESCE(
                CASE 
                    WHEN (pr.schedule_date - pr.ordering_date) < 0 THEN 0 
                    ELSE (pr.schedule_date - pr.ordering_date)
                END, 0) AS delivery_days_avg
        """
        # Esta porcion de código me sirve para traer el promedio en negativo
        # COALESCE(pr.schedule_date - pr.ordering_date, 0) AS delivery_days_avg

    def _from(self):
        return """
        FROM purchase_requisition pr
        """

    def _group_by(self):
        return ""  # No se necesita GROUP BY (cada fila es un requerimiento único)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._select()}
                {self._from()}
            )
        """)

    def action_open_requisitions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Requerimientos',
            'res_model': 'purchase.requisition',
            'view_mode': 'tree,form',
            'domain': [('user_id', '=', self.solicitante_id.id)],
        }