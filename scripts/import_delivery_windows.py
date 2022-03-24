#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import logging
from collections import defaultdict, namedtuple
from datetime import datetime

import click
import click_odoo
import unicodecsv as csv

_logger = logging.getLogger("IMPORT delivery window")

Window = namedtuple("WINDOW", ["day_ids", "start", "end"])

TopCustomer = namedtuple("TOP_CUSTOMER", ["ref", "windows", "rating_level"])


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
            windows = []
            days_by_start_end = defaultdict(list)
            for start, end in (
                ("Lu CLO1", "Lu CLF1"),
                ("Lu CLO2", "Lu CLF2"),
                ("Ma CLO1", "Ma CLF1"),
                ("Ma CLO2", "Ma CLF2"),
                ("Je CLO1", "Je CLF1"),
                ("Je CLO2", "Je CLF2"),
                ("Ve CLO1", "Ve CLF1"),
                ("Ve CLO2", "Ve CLF2"),
            ):
                day = None
                if start.startswith("Lu"):
                    day = self.monday
                elif start.startswith("Ma"):
                    day = self.tuesday
                elif start.startswith("Je"):
                    day = self.thursday
                elif start.startswith("Ve"):
                    day = self.friday
                days_by_start_end[(row[start], row[end])].append(day.id)
            for start_end, day_ids in days_by_start_end.items():
                start = start_end[0]
                end = start_end[1]
                if start.strip() and end.strip():
                    windows.append(Window(day_ids, start, end))
            yield TopCustomer(
                ref=row["ref"], rating_level=row["TOP_rating"], windows=windows
            )

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
        if not top_customer.windows:
            _logger.info("No window defined for %s", top_customer.ref)
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
                        window.start, window.end, window.day_ids,
                    ),
                )
                for window in top_customer.windows
            ]
            values["alc_delivery_window_ids"] = window_values
            partners.write(values)
            _logger.info("%s updated", top_customer.ref)

    def _to_delivery_window_values(self, start, end, day_ids):
        return {
            "start": self._time_str_to_float(start),
            "end": self._time_str_to_float(end),
            "preference": "mandatory",
            "week_day_ids": [(6, 0, day_ids)],
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
