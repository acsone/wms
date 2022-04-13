#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from collections import namedtuple

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT magento user")

CsvLine = namedtuple("CsvLine", ["login", "erp_id", "magento_id"],)


class MagentoUserImporter(object):
    def __init__(self, env, csvfile):
        self.env = env
        self.csvfile = csvfile
        self.error_msgs = []
        self.load_partner_by_ref()
        self.load_magento_logins_by_partner_id()

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

    def load_magento_logins_by_partner_id(self):
        sql = """
               SELECT
                   partner_id,
                   array_agg(username)
               FROM
                   magento_user
               GROUP BY
                   partner_id;
           """
        self.env.cr.execute(sql)
        self._magento_logins_by_partner_id = dict(self.env.cr.fetchall())

    def run(self):
        self.error_msgs = []
        self._reset_all()
        for csv_line in self._iter_read_file():
            self._create_magento_user(csv_line)

    def _reset_all(self):
        pass

    def _iter_read_file(self):
        reader = csv.DictReader(
            self.csvfile, delimiter=",", encoding="utf-8", quotechar='"'
        )
        for row in reader:
            yield CsvLine(**row)

    def _create_magento_user(self, csv_line):
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
        partner_id = partner_id[0]
        logins = self._magento_logins_by_partner_id.get(partner_id, [])
        if csv_line.login not in logins:
            self.env["magento.user"].create(
                {
                    "username": csv_line.login,
                    "partner_id": partner_id,
                    "magento_id": csv_line.magento_id,
                }
            )
            _logger.info(
                "Magento user %s created for partner %s",
                csv_line.login,
                csv_line.erp_id,
            )


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvfile):
    click.echo("Start processing file. . .")
    builder = MagentoUserImporter(env, csvfile)
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
