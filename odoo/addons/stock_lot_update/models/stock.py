# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Jacques-Etienne Baudoux <je@bcim.be>
#    Copyright (C) 2016 BCIM <http://www.bcim.be>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def _get_fk_on(self, table):
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

    def _update_relations(self, product):
        cr = self._cr

        self._get_fk_on("product_product")
        product_fields = dict(cr.fetchall())

        self._get_fk_on("product_template")
        template_fields = dict(cr.fetchall())

        self._get_fk_on(self._table)
        for table, column in cr.fetchall():
            qs = []
            if table in product_fields:
                qs.append("{}={}".format(product_fields[table], product.id))
            if table in template_fields:
                qs.append(
                    "{}={}".format(template_fields[table], product.product_tmpl_id.id)
                )
            if not qs:
                continue

            query = (
                "UPDATE "
                + table
                + " SET "
                + ",".join(qs)
                + " WHERE "
                + column
                + " in %s"
            )
            params = (tuple(self.ids),)

            if table == "stock_move":
                quants = self.env["stock.quant"].search([("lot_id", "in", self.ids)])
                moves = set()
                for quant in quants:
                    moves |= {move.id for move in quant.history_ids}
                if moves:
                    query += " OR id in %s"
                    params += (tuple(moves),)

            cr.execute(query, params)  # pylint: disable=E8103

    @api.multi
    def write(self, vals):
        if not self._context.get("product_noupdate") and vals.get("product_id"):
            for rec in self:
                if rec.product_id == vals["product_id"]:
                    continue
                new_prod = self.env["product.product"].browse(vals["product_id"])
                self._update_relations(new_prod)
                break
        return super(StockProductionLot, self).write(vals)
