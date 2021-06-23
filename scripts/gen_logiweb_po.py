#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from collections import defaultdict

import click
import click_odoo
import unicodecsv as csv

COL_FOURNISSEUR = u"Fournisseur"
COL_REF_LOGIWEB = u"Ref interne"
COL_REF_ALCYON = u"Ref Alcyon"
COL_QTY = u"Qty"

_logger = logging.getLogger("IMPORT INVENTORY")


class InentoryToPoBuilder(object):
    def __init__(self, env, csvfile):
        self.env = env
        self.csvfile = csvfile
        self.error_msgs = []
        self._product_id_by_logiweb_ref = {}
        self._product_id_by_alcyon_ref = {}
        self.logiweb_partner = self.env["res.partner"].search([("ref", "=", "8585")])
        if not self.logiweb_partner:
            raise Exception("Logiweb partner with ref 8585 not found")
        self.load_product_id_by_logiweb_ref()
        self.load_product_id_by_alcyon_ref()
        self.PurchaseOrder = self.env["purchase.order"]
        self.PurchaseOrderLine = self.env["purchase.order.line"]

    def load_product_id_by_logiweb_ref(self):
        _logger.info("Loads logiweb product map")
        sql = """
            SELECT
                replace(imd.name, 'product_logiweb_', ''),
                pp.id
            FROM
                product_product pp
                join product_template pt on pp.product_tmpl_id = pt.id
                join ir_model_data imd on imd.res_id = pt.id and imd.model='product.template'
            WHERE
                imd.name like 'product_logiweb_%'
        """
        self.env.cr.execute(sql)
        self._product_id_by_logiweb_ref = dict(self.env.cr.fetchall())

    def load_product_id_by_alcyon_ref(self):
        _logger.info("Loads alcyon product map")
        sql = """
            SELECT
                default_code,
                id
            FROM
                product_product pp
        """
        self.env.cr.execute(sql)
        self._product_id_by_alcyon_ref = dict(self.env.cr.fetchall())

    def run(self):
        self.error_msgs = []
        inventory_by_supplier = self._map_file_by_supplier()
        _logger.info(
            "Inventory contains %d suppliers and %d lines",
            len(inventory_by_supplier),
            sum([len(item) for item in inventory_by_supplier.values()]),
        )
        for supplier, lines in inventory_by_supplier.items():
            po = self._create_po_from_inventory_for_supplier(supplier, lines)
            _logger.info("PO %s created (id: %s)", po.name, po.id)

    def _map_file_by_supplier(self):
        res = defaultdict(list)
        reader = csv.DictReader(self.csvfile, delimiter=";")
        for row in reader:
            res[row[COL_FOURNISSEUR]].append(row)
        return res

    def _create_po_from_inventory_for_supplier(self, supplier, lines):
        _logger.info(u"Create PO for Logiweb / %s", supplier)
        order_data = {
            "partner_id": self.logiweb_partner.id,
            "partner_ref": u"Inventaire: " + supplier,
        }
        updated_data = self.PurchaseOrder.play_onchanges(order_data, order_data.keys())
        order_data.update(updated_data)
        order_data["order_line"] = [
            (0, 0, line_info) for line_info in self._lines_to_order_line(lines)
        ]
        return self.PurchaseOrder.create(order_data)

    def _lines_to_order_line(self, lines):
        order_line = []
        uom_id = self.env.ref("product.product_uom_unit").id
        for line in lines:
            product_id = self._product_id_by_logiweb_ref.get(line[COL_REF_LOGIWEB])
            product_id = product_id or self._product_id_by_alcyon_ref.get(
                line[COL_REF_ALCYON]
            )
            if not product_id:
                line_info = line.copy()
                line_info["error"] = u"Produit non trouvé en db"
                self.error_msgs.append(line_info)
                continue
            values = {
                "product_id": product_id,
                "name": str(line),
                "product_qty": int(line[COL_QTY]),
                "product_uom": uom_id,
            }
            updated_values = self.PurchaseOrderLine.play_onchanges(
                values, values.keys()
            )
            if not updated_values.get("price_unit"):
                updated_values["price_unit"] = 0.0
            values.update(updated_values)
            order_line.append(values)
        return order_line


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvfile):
    click.echo("Start processing file. . .")
    builder = InentoryToPoBuilder(env, csvfile)
    builder.run()
    if builder.error_msgs:
        with open("erros.csv", "wb") as out_csvfile:
            fieldnames = builder.error_msgs[0].keys()
            writer = csv.DictWriter(out_csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(builder.error_msgs)
            # for msg in builder.error_msgs:
            #    writer.writerows({k:v.encode('utf8') for k,v in msg.items()})
        _logger.info("%d lines not procesed", len(builder.error_msgs))

    env.cr.commit()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
