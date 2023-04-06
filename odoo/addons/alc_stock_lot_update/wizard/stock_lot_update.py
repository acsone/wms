# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_company import Company
from odoo.addons.product.models.product_product import ProductProduct
from odoo.addons.stock.models.stock_lot import StockLot


class StockLotUpdate(models.TransientModel):
    _name = "stock.lot.update"
    _description = "Allow to always modify the product associated to a lot in case"

    lot_id = fields.Many2one[StockLot](string="Lot", compute="_compute_lot_id")
    company_id = fields.Many2one[Company](related="lot_id.company_id")

    product_id = fields.Many2one[ProductProduct](
        string="Product",
        index=True,
        domain=lambda self: self._domain_product_id(),
        required=True,
        check_company=True,
    )

    def action_update(self):
        self._update_product_id()

    @api.model
    def _get_lot_id(self):
        lot_id = self._context.get("active_id")
        return self.env["stock.lot"].browse(lot_id)

    def _compute_lot_id(self):
        lot = self._get_lot_id()
        for rec in self:
            rec.lot_id = lot

    def _domain_product_id(self):
        return self.lot_id._domain_product_id()

    def _update_product_id(self):
        self.ensure_one()
        if self._context.get("product_noupdate"):
            return
        if self.product_id and self.product_id != self.lot_id.product_id:
            self._update_relations(self.product_id)
            self.lot_id.product_id = self.product_id

    def _get_fk_on(self, table) -> None:
        q = """  SELECT cl1.relname as table,
                        att1.attname as column
                   FROM pg_constraint as con, pg_class as cl1, pg_class as cl2,
                        pg_attribute as att1, pg_attribute as att2
                  WHERE con.conrelid = cl1.oid
                    AND con.confrelid = cl2.oid
                    AND array_lower(con.conkey, 1) = 1
                    AND con.conkey[1] = att1.attnum
                    AND att1.attrelid = cl1.oid
                    AND cl2.relname = %s
                    AND att2.attname = 'id'
                    AND array_lower(con.confkey, 1) = 1
                    AND con.confkey[1] = att2.attnum
                    AND att2.attrelid = cl2.oid
                    AND con.contype = 'f'
        """
        return self._cr.execute(q, (table,))

    def _update_relations(self, product) -> None:
        self.ensure_one()
        cr = self._cr

        self._get_fk_on("product_product")
        product_fields = dict(cr.fetchall())

        self._get_fk_on("product_template")
        template_fields = dict(cr.fetchall())

        self._get_fk_on(self.lot_id._table)
        for table, column in cr.fetchall():
            qs = []
            if table in product_fields:
                qs.append(f"{product_fields[table]}={product.id}")
            if table in template_fields:
                qs.append(f"{template_fields[table]}={product.product_tmpl_id.id}")
            if not qs:
                continue

            if table == "stock_move_line":
                move_lines = self.env["stock.move.line"].search(
                    [("lot_id", "=", self.lot_id.id)]
                )
                moves = move_lines.mapped("move_id")
                if len(moves.mapped("move_line_ids.lot_id")) > 1:
                    raise ValidationError(
                        _(
                            "You cannot modify this lot because one of the moves it is associated with is associated with another lot as well."
                        )
                    )
                for move in moves:
                    move.product_id = self.product_id

            query = (
                "UPDATE "
                + table
                + " SET "
                + ",".join(qs)
                + " WHERE "
                + column
                + " in %s"
            )
            params = [(self.lot_id.id,)]

            cr.execute(query, params)
