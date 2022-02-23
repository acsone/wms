#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
from datetime import datetime

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT delivery window")

TopCustomer = namedtuple(
    "TOP_CUSTOMER",
    [
        "ref",
        "name",
        "street",
        "zip",
        "city",
        "partner_longitude",
        "partner_latitude",
        "start_1",
        "end_1",
        "start_2",
        "end_2",
        "start_3",
        "end_3",
        "start_4",
        "end_4",
        "rating_level",
    ],
)


class InentoryToPoBuilder(object):
    def __init__(self, env, csvfile):
        self.env = env
        self.csvfile = csvfile
        self.error_msgs = []
        self.load_partner_by_ref()
        self.ResPartner = self.env["res.partner"]
        self.week_days = self.env["alc.delivery.week.day"].search([])
        self.monday = self.week_days.filtered(lambda d: d.name == "0")
        self.tuesday = self.week_days.filtered(lambda d: d.name == "1")
        self.thursday = self.week_days.filtered(lambda d: d.name == "3")
        self.friday = self.week_days.filtered(lambda d: d.name == "4")
        self.top_400_tag = self.env.ref(
            "__setup__.res_partner_category_top_400", raise_if_not_found=False
        )
        if not self.top_400_tag:
            self.top_400_tag = self.env["res.partner.category"].create(
                {"name": "TOP400"}
            )
            self.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "res_partner_category_top_400",
                    "model": self.top_400_tag._name,
                    "res_id": self.top_400_tag.id,
                }
            )
        self.top_800_tag = self.env.ref(
            "__setup__.res_partner_category_top_800", raise_if_not_found=False
        )
        if not self.top_800_tag:
            self.top_800_tag = self.env["res.partner.category"].create(
                {"name": "TOP800"}
            )
            self.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "res_partner_category_top_800",
                    "model": self.top_800_tag._name,
                    "res_id": self.top_800_tag.id,
                }
            )
        self.top_2000_tag = self.env.ref(
            "__setup__.res_partner_category_top_2000", raise_if_not_found=False
        )
        if not self.top_2000_tag:
            self.top_2000_tag = self.env["res.partner.category"].create(
                {"name": "TOP2000"}
            )
            self.env["ir.model.data"].create(
                {
                    "module": "__setup__",
                    "name": "res_partner_category_top_2000",
                    "model": self.top_2000_tag._name,
                    "res_id": self.top_2000_tag.id,
                }
            )

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

    def run(self):
        self.error_msgs = []
        self._reset_all()
        for top_customer in self._iter_read_file():
            self._define_delivery_window(top_customer)

    def _reset_all(self):
        self.env["alc.delivery.window"].search([]).unlink()

    def _reset_top_400(self):
        top_400_partners = self.env["res.partner"].search(
            [("category_id", "in", self.top_400_tag.ids)]
        )
        _logger.info("Found %d top_400 to reset", len(top_400_partners))
        top_400_partners.mapped("alc_delivery_window_ids").unlink()
        top_400_partners.write({"category_id": [(3, self.top_400_tag.id)]})

    def _iter_read_file(self):
        reader = csv.DictReader(self.csvfile, delimiter=";")
        for row in reader:
            yield TopCustomer(**row)

    def _define_delivery_window(self, top_customer):
        ids = self._partner_ids_by_ref.get(top_customer.ref)
        if not ids:
            info = top_customer._asdict()
            info["error"] = "No record found"
            self.error_msgs.append(info)
            _logger.error("Record not found for ref %s", top_customer.ref)
            return
        partners = self.ResPartner.browse(ids)
        values = {"alc_delivery_window_ids": [(5, None, None)]}
        if (
            top_customer.rating_level == "TOP400"
            and self.top_400_tag not in partners.mapped("category_id")
        ):
            values["category_id"] = [(4, self.top_400_tag.id)]
        if (
            top_customer.rating_level == "TOP800"
            and self.top_800_tag not in partners.mapped("category_id")
        ):
            values["category_id"] = [(4, self.top_800_tag.id)]
        if (
            top_customer.rating_level == "TOP2000"
            and self.top_2000_tag not in partners.mapped("category_id")
        ):
            values["category_id"] = [(4, self.top_2000_tag.id)]
        if not top_customer.start_1 and not top_customer.start_2:
            _logger.info("No window defined for %s", top_customer.name)
            if values:
                partners.write(values)
            return

        partners.mapped("alc_delivery_window_ids").unlink()
        if top_customer.rating_level == "TOP400":
            window_values = [
                (
                    0,
                    0,
                    self._to_delivery_window_values(
                        top_customer.start_1,
                        top_customer.end_1,
                        self.monday | self.thursday,
                    ),
                )
            ]
            if top_customer.start_2:
                window_values.append(
                    (
                        0,
                        0,
                        self._to_delivery_window_values(
                            top_customer.start_2,
                            top_customer.end_2,
                            self.monday | self.thursday,
                        ),
                    )
                )
            if top_customer.start_3:
                window_values.append(
                    (
                        0,
                        0,
                        self._to_delivery_window_values(
                            top_customer.start_3,
                            top_customer.end_3,
                            self.tuesday | self.friday,
                        ),
                    )
                )
            if top_customer.start_4:
                window_values.append(
                    (
                        0,
                        0,
                        self._to_delivery_window_values(
                            top_customer.start_4,
                            top_customer.end_4,
                            self.tuesday | self.friday,
                        ),
                    )
                )
            values["alc_delivery_window_ids"] = window_values
            partners.write(values)
            _logger.info("%s updated", top_customer.name)

    def _to_delivery_window_values(self, start, end, days):
        return {
            "start": self._time_str_to_float(start),
            "end": self._time_str_to_float(end),
            "preference": "mandatory",
            "week_day_ids": [(6, 0, days.ids)],
        }

    def _time_str_to_float(self, time_str):
        # dt = datetime.strptime(time_str, "%I:%M:%S %p")
        dt = datetime.strptime(time_str, "%H:%M")
        return dt.hour + dt.minute / 60.0


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
