# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openerp import api, fields, models, tools
from openerp.osv.expression import AND, OR
from psycopg2.extensions import AsIs


class WizardValuationHistory(models.TransientModel):
    _inherit = "wizard.valuation.history"

    date = fields.Datetime(default=lambda self: self._default_date())

    def _default_date(self):
        materialized_model = self.env["stock.history.materialized"]
        refresh_date = materialized_model.get_refresh_date()
        return refresh_date or fields.Datetime.now()

    @api.multi
    def open_table(self):
        materialized_model = self.env["stock.history.materialized"]
        refresh_date = materialized_model.get_refresh_date()
        date_dt = fields.Datetime.from_string(self.date)
        if not refresh_date or date_dt > fields.Datetime.from_string(refresh_date):
            materialized_model.refresh_view()
        res = super(WizardValuationHistory, self).open_table()
        res["context"]["search_default_group_by_product"] = False
        res["context"]["search_default_group_by_location"] = False
        now = fields.Datetime.now()
        domain = AND([[("date", ">=", self.date)], [("date", "<=", now)]])
        domain = OR([domain, [("move_id", "=", False)]])

        res["domain"] = domain

        return res


class StockHistoryMaterialized(models.AbstractModel):
    _name = "stock.history.materialized"

    @api.model
    def get_refresh_date(self):
        return self.env["ir.config_parameter"].get_param("stock_history_refresh_date")

    @api.model
    def set_refresh_date(self, date=None):
        if date is None:
            date = fields.Datetime.now()
        self.env["ir.config_parameter"].set_param("stock_history_refresh_date", date)

    @api.model
    def refresh_view(self):
        self.env.cr.execute("refresh materialized view %s", (AsIs(self._table),))
        self.set_refresh_date()

    def init(self):
        self.env.cr.execute(
            "DROP MATERIALIZED VIEW IF EXISTS %s CASCADE", (AsIs(self._table),)
        )
        self.env.cr.execute(
            """
            CREATE MATERIALIZED VIEW %s AS (
              SELECT MIN(id) AS id,
                move_id,
                location_id,
                company_id,
                product_id,
                product_categ_id,
                product_template_id,
                product_supplier_id,
                SUM(quantity) as quantity,
                date,
                COALESCE(SUM(price_unit_on_quant * quantity) / NULLIF(SUM(quantity), 0), 0) AS price_unit_on_quant,
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
                    -quant.qty AS quantity,
                    stock_move.date AS date,
                    coalesce(nullif(stock_move.price_unit, 0), pph.cost) AS price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant AS quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN LATERAL
                    (SELECT distinct on (product_id) cost
                    FROM product_price_history pph
                    WHERE pph.product_id = quant.product_id
                      AND pph.datetime <= stock_move.date
                    ORDER BY product_id, datetime DESC, id DESC
                    ) pph on TRUE
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
                WHERE quant.qty > 0 AND stock_move.state = 'done'
                AND dest_location.usage IN ('internal', 'transit', 'view')
                AND (
                    source_location.company_id != dest_location.company_id OR
                    source_location.usage NOT IN ('internal', 'transit', 'view')
                 )
                ) UNION ALL
                (SELECT
                    (-1) * stock_move.id AS id,
                    stock_move.id AS move_id,
                    source_location.id AS location_id,
                    source_location.company_id AS company_id,
                    stock_move.product_id AS product_id,
                    product_template.id AS product_template_id,
                    product_template.supplier_id AS product_supplier_id,
                    product_template.categ_id AS product_categ_id,
                    quant.qty AS quantity,
                    stock_move.date AS date,
                    coalesce(nullif(stock_move.price_unit, 0), pph.cost) as price_unit_on_quant,
                    stock_move.origin AS source,
                    stock_production_lot.name AS serial_number
                FROM
                    stock_quant AS quant
                JOIN
                    stock_quant_move_rel ON stock_quant_move_rel.quant_id = quant.id
                JOIN
                    stock_move ON stock_move.id = stock_quant_move_rel.move_id
                LEFT JOIN LATERAL
                    (SELECT distinct on (product_id) cost
                    FROM product_price_history pph
                    WHERE pph.product_id = quant.product_id
                      AND pph.datetime <= stock_move.date
                    ORDER BY product_id, datetime DESC, id DESC
                    ) pph on TRUE
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
                WHERE quant.qty > 0 AND stock_move.state = 'done'
                  AND source_location.usage in ('internal', 'transit', 'view') AND stock_quant_move_rel.quant_id = quant.id
                AND (
                    dest_location.company_id != source_location.company_id OR
                    dest_location.usage NOT IN ('internal', 'transit', 'view')
                     )
                )

            UNION ALL
            (
            /* One record for each product current stock */
                SELECT
                     2147483646 - quant.product_id as id,
                    NULL AS move_id,
                    NULL AS location_id,
                    quant.company_id,
                    quant.product_id as product_id,
                    product_template.id AS product_template_id,
                    product_template.supplier_id AS product_supplier_id,
                    product_template.categ_id AS product_categ_id,
                    sum(quant.qty) AS quantity,
                    now() AS date,
                    MIN(pph.cost) as price_unit_on_quant,
                    'Current stock valuation' AS source,
                    NULL AS serial_number
                    FROM
                    stock_quant as quant
                    JOIN
                    stock_location quant_location ON quant_location.id = quant.location_id
                    JOIN
                    product_product ON product_product.id = quant.product_id
                    JOIN
                    product_template ON product_template.id = product_product.product_tmpl_id
                    LEFT JOIN LATERAL
                        (SELECT distinct on (product_id) cost
                        FROM product_price_history pph
                        WHERE pph.product_id = quant.product_id
                          AND pph.datetime <= now()
                        ORDER BY product_id, datetime DESC, id DESC
                        ) pph on TRUE
                    WHERE quant_location.usage = 'internal'
                    GROUP BY (quant.product_id, quant.company_id, product_template.id)
               )
            )

                AS foo
                GROUP BY move_id, location_id, company_id, product_id,
                         product_categ_id, product_supplier_id, date,
                         source, product_template_id
            ) WITH NO DATA;""",
            (AsIs(self._table),),
        )
        # pylint: disable=sql-injection
        self.env.cr.execute(
            "CREATE UNIQUE INDEX pk_{} ON {} (id)".format(self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX %s_location_id_idx ON %s (location_id)"
            % (self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX %s_product_id_idx ON %s (product_id)"
            % (self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX %s_product_categ_id_idx ON %s (product_categ_id)"
            % (self._table, self._table)
        )
        self.env.cr.execute(
            "CREATE INDEX {}_date_idx ON {} (date)".format(self._table, self._table)
        )
        self.set_refresh_date(date=False)
        cron = self.env.ref(
            "stock_valuation.refresh_materialized_view",
            # at install, won't exist yet
            raise_if_not_found=False,
        )
        # refresh data asap, but not during the upgrade
        if cron:
            cron.nextcall = fields.Datetime.now()


class StockHistory(models.Model):
    _inherit = "stock.history"

    cost_method = fields.Char(related="product_id.cost_method", readonly=True)
    product_supplier_id = fields.Many2one("res.partner", "Supplier", readonly=True)

    product_last_in_date = fields.Datetime(
        "Last Purchasing Date", related="product_id.product_last_in_date"
    )
    product_last_out_date = fields.Datetime(
        "Last Selling Date", related="product_id.product_last_out_date"
    )

    def _compute_inventory_value(self):
        history_date = self._context.get("history_date", fields.Datetime.now())
        for rec in self:
            # get price_unit at date from product_price_history
            history_price = rec.product_id.get_history_price(
                rec.company_id.id, date=history_date
            )
            rec.inventory_value = rec.quantity * history_price

    # pylint: disable=redefined-outer-name
    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        if "inventory_value" in fields:
            fields.remove("inventory_value")
        res = super(StockHistory, self).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        return res

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        # We do not create the materialized view with the
        # name "stock_history" because an upgrade of the
        # stock_account would fail.
        # Use an indirection with another model.
        self.env.cr.execute(
            """
            CREATE OR REPLACE VIEW stock_history AS (
                SELECT * FROM stock_history_materialized
            )
        """
        )
