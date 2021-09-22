#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging

import click
import click_odoo
import unicodecsv as csv

from odoo import fields

_logger = logging.getLogger("Geocode partner")


def _iter_read_file(csvfile):
    reader = csv.DictReader(csvfile, delimiter=",")
    for row in reader:
        yield row


@click.command()
@click.option("csvfile", "--csv-file", type=click.File(mode="rb"), required=True)
@click_odoo.env_options(default_log_level="info")
def main(env, csvfile):
    click.echo("Start processing file. . .")
    ResPartner = env["res.partner"]
    for row in _iter_read_file(csvfile):
        partner = ResPartner.browse(int(row["id"]))
        partner.write(
            {
                "partner_latitude": row["lat"],
                "partner_longitude": row["lon"],
                "date_localization": fields.Date.context_today(partner),
            }
        )
    env.cr.commit()


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
