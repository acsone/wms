# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, tools, models, fields


class WizardValuationHistory(models.TransientModel):
    _inherit = 'wizard.valuation.history'

    date = fields.Datetime(default=lambda self: self._default_date())

    def _default_date(self):
        materialized_model = self.env['stock.history.materialized']
        refresh_date = materialized_model.get_refresh_date()
        return refresh_date or fields.Datetime.now()

    @api.multi
    def open_table(self):
        materialized_model = self.env['stock.history.materialized']
        refresh_date = materialized_model.get_refresh_date()
        if (not refresh_date or
                fields.Datetime.from_string(self.date) >
                fields.Datetime.from_string(refresh_date)):
            materialized_model.refresh_view()
        res = super(WizardValuationHistory, self).open_table()
        res['context']['search_default_group_by_product'] = False
        res['context']['search_default_group_by_location'] = False
        return res


class StockHistoryMaterialized(models.AbstractModel):
    _name = 'stock.history.materialized'

    @api.model
    def get_refresh_date(self):
        return self.env['ir.config_parameter'].get_param(
            'stock_history_refresh_date'
        )

    @api.model
    def set_refresh_date(self, date=None):
        if date is None:
            date = fields.Datetime.now()
        self.env['ir.config_parameter'].set_param(
            'stock_history_refresh_date', date
        )

    @api.model
    def refresh_view(self):
        self.env.cr.execute('refresh materialized view %s' % self._table)
        self.set_refresh_date()

    def init(self):
        self.env.cr.execute(
            "DROP MATERIALIZED VIEW IF EXISTS %s CASCADE" % self._table
        )
        self.env.cr.execute("""
            CREATE MATERIALIZED VIEW %s AS (
              WITH internal AS (
                SELECT parent_left, parent_right
                FROM stock_location
                WHERE id = (SELECT res_id
                            FROM ir_model_data
                            WHERE module = 'specific_base'
                            AND name = 'stock_location_vlb')
              ),
              -- we want to valorize the goods in the output too
              output AS (
                SELECT res_id as id FROM ir_model_data
                WHERE module = 'stock' AND name = 'stock_location_output'
              )
              SELECT MIN(id) as id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                product_template_id,
                product_supplier_id,
                SUM(quantity) as quantity,
                date,
                COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) as price_unit_on_quant,
                source,
                string_agg(DISTINCT serial_number, ', ' ORDER BY serial_number) AS serial_number
                FROM
                ((SELECT
                    stock_move.id AS id,
                    stock_move.id AS move_id,
                    dest_location.id AS location_id,
                    dest_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.supplier_id AS product_supplier_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done'
                    AND (dest_location.id = (SELECT id FROM output) OR
                         dest_location.parent_left >= (SELECT parent_left FROM internal) AND
                         dest_location.parent_right <= (SELECT parent_right FROM internal)
                         )
                AND (
                    not (source_location.company_id is null and dest_location.company_id is null) or
                    source_location.company_id != dest_location.company_id or
                    (source_location.id != (SELECT id FROM output) AND
                     (source_location.parent_left < (SELECT parent_left FROM internal) OR
                      source_location.parent_right > (SELECT parent_right FROM internal))))
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.categ_id AS product_categ_id,
                    product_template.supplier_id AS product_supplier_id,
                    - quant.qty AS quantity,
                    stock_move.date AS date,
                    quant.cost as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant as quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN
                    stock_production_lot ON stock_production_lot.id = quant.lot_id
                JOIN
                    stock_location source_location ON stock_move.location_id = source_location.id
                JOIN
                    stock_location dest_location ON stock_move.location_dest_id = dest_location.id
                JOIN
                    product_product ON product_product.id = stock_move.product_id
                JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                WHERE quant.qty>0 AND stock_move.state = 'done'
                AND (source_location.id = (SELECT id FROM output) OR
                     source_location.parent_left >= (SELECT parent_left FROM internal) AND
                     source_location.parent_right <= (SELECT parent_right FROM internal)
                     )
                AND (
                    not (dest_location.company_id is null and source_location.company_id is null) or
                    dest_location.company_id != source_location.company_id or
                    (dest_location.id != (SELECT id FROM output) AND
                     (dest_location.parent_left < (SELECT parent_left FROM internal) OR
                     dest_location.parent_right > (SELECT parent_right FROM internal))))
                ))
                AS foo
                GROUP BY move_id, location_id, company_id, product_id,
                         product_categ_id, product_supplier_id, date,
                         source, product_template_id
            ) WITH NO DATA;""" % (self._table,))  # noqa
        self.env.cr.execute(
            "CREATE UNIQUE INDEX pk_%s ON %s (id)" % (self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX %s_location_id ON %s (location_id)" %
            (self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX %s_product_id ON %s (product_id)" %
            (self._table, self._table)
        )
        self.set_refresh_date(date=False)
        cron = self.env.ref(
            'stock_valuation.refresh_materialized_view',
            # at install, won't exist yet
            raise_if_not_found=False
        )
        # refresh data asap, but not during the upgrade
        if cron:
            cron.nextcall = fields.Datetime.now()


class StockHistory(models.Model):
    _inherit = 'stock.history'

    cost_method = fields.Char(related='product_id.cost_method', readonly=True)
    product_supplier_id = fields.Many2one(
        'res.partner', 'Supplier', readonly=True)

    product_last_in_date = fields.Datetime(
        'Last Purchasing Date',
        compute='_get_product_last_in_date')
    product_last_out_date = fields.Datetime(
        'Last Selling Date',
        compute='_get_product_last_out_date')

    def _get_product_last_in_date(self):
        if 'history_date' not in self._context:
            return
        self._cr.execute("""
            SELECT DISTINCT ON (product_id)
                purchase_order_line.product_id,
                purchase_order.date_order
            FROM purchase_order_line
            LEFT JOIN purchase_order
                ON purchase_order_line.order_id=purchase_order.id
            WHERE price_unit > 0
              AND purchase_order.date_order <= %s
              AND purchase_order_line.state in ('purchase', 'done')
            ORDER BY
                purchase_order_line.product_id,
                purchase_order.date_order desc
            """, (self._context['history_date'],))
        dates_by_product = dict(self._cr.fetchall())
        for rec in self:
            rec.product_last_in_date = dates_by_product.get(
                rec.product_id.id, False)

    def _get_product_last_out_date(self):
        if 'history_date' not in self._context:
            return
        self._cr.execute("""
            SELECT DISTINCT ON (product_id)
                sale_order_line.product_id,
                sale_order.confirmation_date
            FROM sale_order_line
            LEFT JOIN sale_order
                ON sale_order_line.order_id=sale_order.id
            WHERE price_unit > 0
              AND confirmation_date <= %s
              AND sale_order_line.state != 'cancel'
            ORDER BY
                sale_order_line.product_id,
                sale_order.confirmation_date desc
            """, (self._context['history_date'],))
        dates_by_product = dict(self._cr.fetchall())
        for rec in self:
            rec.product_last_out_date = dates_by_product.get(
                rec.product_id.id, False)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # We do not create the materialized view with the
        # name "stock_history" because an upgrade of the
        # stock_account would fail.
        # Use an indirection with another model.
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW stock_history AS (
                SELECT * FROM stock_history_materialized
            )
        """)
