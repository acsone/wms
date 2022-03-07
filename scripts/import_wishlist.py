#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict, namedtuple

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT wishlist")

CsvLine = namedtuple(
    "CsvLine", ["customer", "erp_id", "wishlist_name", "product_sku", "product_name"],
)


class WhishlistImporter(object):
    def __init__(self, env, csvfile):
        self.env = env
        self.csvfile = csvfile
        self.error_msgs = []
        self.load_partner_by_ref()
        self.load_wishlist_by_partner()
        self.load_product_id_by_sku()

    def load_partner_by_ref(self):
        _logger.info("Loads partner by ref")
        sql = """
            SELECT
                ref,
                array_agg(id)
            FROM
                res_partner
            WHERE
                active
                and not is_b2c_customer
            GROUP BY
                ref;
        """
        self.env.cr.execute(sql)
        self._partner_ids_by_ref = dict(self.env.cr.fetchall())

    def load_wishlist_by_partner(self):
        _logger.info("Loads wishlist by partner")
        sql = """
            SELECT
                id,
                name,
                partner_id
            FROM
                product_set
            WHERE
                typology = 'wishlist'
        """
        self.env.cr.execute(sql)
        self.wishlist_by_partner = defaultdict(dict)
        for _id, name, partner_id in self.env.cr.fetchall():
            self.wishlist_by_partner[partner_id][name] = _id

    def load_product_id_by_sku(self):
        _logger.info("Loads product_id by sku")
        sql = """
            SELECT
                default_code,
                id
            FROM
                product_product
        """
        self.env.cr.execute(sql)
        self._product_id_by_sku = dict(self.env.cr.fetchall())

    def run(self):
        self.error_msgs = []
        self._reset_all()
        for csv_line in self._iter_read_file():
            self._create_wishlist(csv_line)

    def _reset_all(self):
        pass

    def _iter_read_file(self):
        reader = csv.DictReader(
            self.csvfile, delimiter=",", encoding="utf-8", quotechar='"'
        )
        for row in reader:
            yield CsvLine(**row)

    def _create_wishlist(self, csv_line):
        partner_id = self._partner_ids_by_ref.get(str(csv_line.erp_id))
        if not partner_id:
            info = csv_line._asdict()
            info["error"] = "Partner not found %s" % csv_line.erp_id
            self.error_msgs.append(info)
            _logger.error("Record not found for ref %s", csv_line.erp_id)
            return
        if len(partner_id) > 1:
            info = csv_line._asdict()
            info["error"] = "More than 1 partner found for ref"
            self.error_msgs.append(info)
            _logger.error(
                "More than 1 partner found  (%s) for ref %s",
                partner_id,
                csv_line.erp_id,
            )
            return
        partner_id = partner_id[0]
        product_id = self._product_id_by_sku.get(csv_line.product_sku)
        if not product_id:
            info = csv_line._asdict()
            info["error"] = "Product not found"
            self.error_msgs.append(info)
            return
        list_id = self.wishlist_by_partner[csv_line.erp_id].get(csv_line.wishlist_name)
        if not list_id:
            list_id = (
                self.env["product.set"]
                .create(
                    {
                        "name": csv_line.wishlist_name,
                        "partner_id": partner_id,
                        "typology": "wishlist",
                    }
                )
                .id
            )
            self.wishlist_by_partner[csv_line.erp_id][csv_line.wishlist_name] = list_id
        wlist = self.env["product.set"].browse(list_id)
        if product_id not in wlist.mapped("set_line_ids.product_id").ids:
            self.env["product.set.line"].create(
                {"product_id": product_id, "product_set_id": list_id}
            )
            _logger.info(
                "Product %s added to wishlist %s",
                csv_line.product_sku,
                csv_line.wishlist_name,
            )


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvfile):
    click.echo("Start processing file. . .")
    builder = WhishlistImporter(env, csvfile)
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
