# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import itertools
import logging
from collections import defaultdict, namedtuple

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

Window = namedtuple("WINDOW", ["day_ids", "start", "end"])

TopCustomer = namedtuple("TOP_CUSTOMER", ["ref", "windows", "rating_level"])

EXPECTED_COLUMNS = {
    "code",
    "Lu CLO1",
    "Lu CLF1",
    "Lu CLO2",
    "Lu CLF2",
    "Ma CLO1",
    "Ma CLF1",
    "Ma CLO2",
    "Ma CLF2",
    "Me CLO1",
    "Me CLF1",
    "Me CLO2",
    "Me CLF2",
    "Je CLO1",
    "Je CLF1",
    "Je CLO2",
    "Je CLF2",
    "Ve CLO1",
    "Ve CLF1",
    "Ve CLO2",
    "Ve CLF2",
    "TOP_rating",
}


class AlcDeliveryWindowImporter(models.TransientModel):

    _name = "alc.delivery.window.importer"

    document = fields.Binary(string="XLSX file", required=True)
    description = fields.Html(readonly=True, default=lambda a: a._get_description(),)

    @api.model
    def _get_description(self):
        return _(
            """
<p>The XLSX file must contains the following columns: {headers}</p>
<p>The hours values must be datetime columns</p>
<p><b>Lines with an unknow partner reference (code) will be ignored</b></p>
"""
        ).format(headers=", ".join(EXPECTED_COLUMNS))

    @api.multi
    def doit(self):
        # pylint: disable=deprecated-method
        self.ensure_one()
        now = fields.Datetime.now()
        content = base64.decodestring(self.document)
        importer = _DeliveryWindowImporter(self.env, content)
        importer.run()
        action = {
            "type": "ir.actions.act_window",
            "name": _("Updated partners"),
            "res_model": "res.partner",
            "domain": [("write_date", ">=", now)],
            "view_mode": "tree,form",
        }
        return action


class _DeliveryWindowImporter(object):
    def __init__(self, env, xlsx_content):
        self.env = env
        self.xlsx_content = xlsx_content
        self.error_msgs = []
        self.load_partner_by_ref()
        self.ResPartner = self.env["res.partner"]
        self.week_days = self.env["alc.delivery.week.day"].search([])
        self.monday = self.week_days.filtered(lambda d: d.name == "0")
        self.tuesday = self.week_days.filtered(lambda d: d.name == "1")
        self.wednesday = self.week_days.filtered(lambda d: d.name == "2")
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
        book = xlrd.open_workbook(file_contents=self.xlsx_content, on_demand=True)
        try:
            iterator = self._read_xls_book(book)
            headers = next(iterator)  # pylint: disable=stop-iteration-return
            missing_headers = EXPECTED_COLUMNS - set(headers)
            if missing_headers:
                raise ValidationError(
                    _("The xlsx file doesn't contains columns %s") % missing_headers
                )
            for values in iterator:
                row = dict(zip(headers, values))
                windows = []
                days_by_start_end = defaultdict(list)
                for start, end in (
                    ("Lu CLO1", "Lu CLF1"),
                    ("Lu CLO2", "Lu CLF2"),
                    ("Ma CLO1", "Ma CLF1"),
                    ("Ma CLO2", "Ma CLF2"),
                    ("Me CLO1", "Me CLF1"),
                    ("Me CLO2", "Me CLF2"),
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
                    elif start.startswith("Me"):
                        day = self.wednesday
                    elif start.startswith("Je"):
                        day = self.thursday
                    elif start.startswith("Ve"):
                        day = self.friday
                    days_by_start_end[(row[start], row[end])].append(day.id)
                for start_end, day_ids in days_by_start_end.items():
                    start = start_end[0]
                    end = start_end[1]
                    if start and end:
                        windows.append(Window(day_ids, start, end))
                yield TopCustomer(
                    ref=row["code"], rating_level=row["TOP_rating"], windows=windows,
                )
        finally:
            book.release_resources()
            del book

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
            "start": self._dt_to_float(start),
            "end": self._dt_to_float(end),
            "preference": "mandatory",
            "week_day_ids": [(6, 0, day_ids)],
        }

    def _dt_to_float(self, dt):
        return dt.hour + dt.minute / 60.0

    def _read_xls_book(self, book):
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        for row in itertools.imap(sheet.row, range(sheet.nrows)):
            values = []
            for cell in row:
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        unicode(cell.value) if is_float else unicode(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    dt = xlrd.xldate.xldate_as_datetime(cell.value, book.datemode)
                    values.append(dt)
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u"True" if cell.value else u"False")
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Error cell found while reading XLS/XLSX file: %s")
                        % xlrd.error_text_from_code.get(
                            cell.value, "unknown error code %s" % cell.value
                        )
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values
