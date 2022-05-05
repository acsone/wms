#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT wishlist")


class ProductUpdater(object):
    def __init__(self, env, csvamm, csvcnk):
        self.env = env
        self.csvcnk = csvcnk
        self.csvamm = csvamm

    def _get_cnk_by_template_id(self):
        self.env.cr.execute(
            """
            select id, cnk_code from product_template where active=true
        """
        )
        return dict(self.env.cr.fetchall())

    def _get_amm_by_template_id(self):
        self.env.cr.execute(
            """
            select id, code_amm from product_template where active=true
        """
        )
        return dict(self.env.cr.fetchall())

    def run(self):
        old_cnk_codes = self._get_cnk_by_template_id()
        new_cnk_codes = {}
        for csv_line in self._iter_read_file(self.csvcnk):
            product_id = int(csv_line["ID"])
            cnk_code = csv_line["CNK"].strip()
            new_cnk_codes[product_id] = cnk_code
        for tmpl_id, old_cnk_code in old_cnk_codes.items():
            new_code = new_cnk_codes.get(tmpl_id)
            if old_cnk_code != new_code:
                product = self.env["product.template"].browse(tmpl_id)
                if not product.active or not new_code:
                    continue
                _logger.info(
                    "Update %s product %s cnk: '%s' -> '%s'   ",
                    tmpl_id,
                    product.default_code,
                    product.cnk_code,
                    new_code,
                )
                product.cnk_code = new_code
        old_amm_codes = self._get_amm_by_template_id()
        new_amm_codes = {}
        for csv_line in self._iter_read_file(self.csvamm):
            product_id = int(csv_line["ID"])
            code_amm = csv_line["AMM"].strip()
            new_amm_codes[product_id] = code_amm
        for tmpl_id, old_amm_code in old_amm_codes.items():
            new_code = new_amm_codes.get(tmpl_id)
            if old_amm_code != new_code:
                product = self.env["product.template"].browse(tmpl_id)
                if not product.active or not new_code:
                    continue
                _logger.info(
                    "Update product %s amm: '%s' -> '%s'   ",
                    product.default_code,
                    product.code_amm,
                    new_code,
                )
                product.code_amm = new_code
                self.env.cr.commit()  # pylint: disable=invalid-commit

    def _iter_read_file(self, csvfile):
        reader = csv.DictReader(csvfile, delimiter=",", encoding="utf-8", quotechar='"')
        for row in reader:
            yield row


@click.command()
@click.option("csvamm", "--csv-amm", type=click.File(mode="rb"), required=True)
@click.option("csvcnk", "--csv-cnk", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvamm, csvcnk):
    click.echo("Start processing file. . .")
    builder = ProductUpdater(env, csvamm, csvcnk)
    builder.run()
    env.cr.commit()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
