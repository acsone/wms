#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from collections import namedtuple

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT product subscription")

CsvLine = namedtuple("CsvLine", ["erp_id", "product_sku"],)


class PromotionSubscriptionImporter(object):
    def __init__(self, env, csvfile):
        self.env = env
        self.csvfile = csvfile
        self.error_msgs = []
        self.load_partner_by_ref()
        self.load_product_tmpl_id_by_sku()
        self.load_subcribed_product_tmpl_ids_by_partner_id()
        self.load_product_id_by_tmpl_id()

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
        sql = """
            SELECT
                ref,
                array_agg(id)
            FROM
                res_partner
            WHERE
                not active
                and not is_b2c_customer
            GROUP BY
                ref;
        """
        self.env.cr.execute(sql)
        self._inactive_partner_ids_by_ref = dict(self.env.cr.fetchall())

    def load_subcribed_product_tmpl_ids_by_partner_id(self):
        sql = """
               SELECT
                   partner_id,
                   array_agg(product_tmpl_id)
               FROM
                   alc_product_promotion_subscription
               GROUP BY
                   partner_id;
           """
        self.env.cr.execute(sql)
        self._subcribed_product_tmpl_ids_by_partner_id = dict(self.env.cr.fetchall())

    def load_product_tmpl_id_by_sku(self):
        sql = """
            SELECT
                default_code,
                id
            FROM
                product_template
        """
        self.env.cr.execute(sql)
        self._product_tmpl_id_by_sku = dict(self.env.cr.fetchall())

    def load_product_id_by_tmpl_id(self):
        sql = """
            SELECT
                distinct on (id)
                product_tmpl_id,
                id
            FROM
                product_product
            ORDER BY id;
        """
        self.env.cr.execute(sql)
        self._product_id_by_tmpl_id = dict(self.env.cr.fetchall())

    def run(self):
        self.error_msgs = []
        for csv_line in self._iter_read_file():
            self._create_promotion_subscription(csv_line)

    def _iter_read_file(self):
        reader = csv.DictReader(
            self.csvfile, delimiter=",", encoding="utf-8", quotechar='"'
        )
        for row in reader:
            yield CsvLine(**row)

    def _create_promotion_subscription(self, csv_line):
        partner_id = self._partner_ids_by_ref.get(str(csv_line.erp_id))
        if not partner_id and str(csv_line.erp_id) in self._inactive_partner_ids_by_ref:
            _logger.info("Inactive partner for ref %s", csv_line.erp_id)
            return
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
        product_tmpl_id = self._product_tmpl_id_by_sku.get(csv_line.product_sku)
        if not product_tmpl_id:
            info = csv_line._asdict()
            info["error"] = "Product not found %s" % csv_line.product_sku
            self.error_msgs.append(info)
            return

        partner_id = partner_id[0]
        subscriptions = self._subcribed_product_tmpl_ids_by_partner_id.get(
            partner_id, []
        )
        if product_tmpl_id not in subscriptions:
            self.env["alc.product.promotion.subscription"].create(
                {
                    "partner_id": partner_id,
                    "product_id": self._product_id_by_tmpl_id[product_tmpl_id],
                }
            )
            _logger.info(
                "Subscription to product sku %s created for partner %s",
                csv_line.product_sku,
                csv_line.erp_id,
            )


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvfile):
    click.echo("Start processing file. . .")
    builder = PromotionSubscriptionImporter(env, csvfile)
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
