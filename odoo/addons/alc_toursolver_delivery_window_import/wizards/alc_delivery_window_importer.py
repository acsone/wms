# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import logging
from collections import defaultdict, namedtuple

import xlrd

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)

Window = namedtuple("WINDOW", ["day_ids", "start", "end"])

TopCustomer = namedtuple("TOP_CUSTOMER", ["ref", "windows"])

EXPECTED_COLUMNS = {
    "code",
    "mon_start1",
    "mon_end1",
    "mon_start2",
    "mon_end2",
    "tue_start1",
    "tue_end1",
    "tue_start2",
    "tue_end2",
    "wed_start1",
    "wed_end1",
    "wed_start2",
    "wed_end2",
    "thu_start1",
    "thu_end1",
    "thu_start2",
    "thu_end2",
    "fri_start1",
    "fri_end1",
    "fri_start2",
    "fri_end2",
}


class AlcDeliveryWindowImporter(models.TransientModel):

    _name = "alc.delivery.window.importer"
    _description = "Import delivery window from XLSX file"

    document = fields.Binary(string="XLSX file", required=True)
    description = fields.Html(
        readonly=True,
        default=lambda a: a._get_description(),
    )

    @api.model
    def _get_description(self):
        return _(
            """
<p>The XLSX file must contains the following columns: {headers}</p>
<p>The hours values must be datetime columns</p>
<p><b>Lines with an unknow partner reference (code) will be ignored</b></p>
"""
        ).format(headers=", ".join(EXPECTED_COLUMNS))

    def doit(self):
        self.ensure_one()
        now = fields.Datetime.now()
        content = base64.b64decode(self.document)
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


class _DeliveryWindowImporter:
    def __init__(self, env, xlsx_content):
        self.env = env
        self.xlsx_content = xlsx_content
        self.error_msgs = []
        self.load_partner_by_ref()
        self.ResPartner = self.env["res.partner"]
        self.week_days = self.env["time.weekday"].search([])
        self.monday = self.week_days.filtered(lambda d: d.name == "0")
        self.tuesday = self.week_days.filtered(lambda d: d.name == "1")
        self.wednesday = self.week_days.filtered(lambda d: d.name == "2")
        self.thursday = self.week_days.filtered(lambda d: d.name == "3")
        self.friday = self.week_days.filtered(lambda d: d.name == "4")

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
        self.env["toursolver.delivery.window"].search([]).unlink()

    def _iter_read_file(self):  # noqa: c901
        book = xlrd.open_workbook(file_contents=self.xlsx_content, on_demand=True)
        try:
            iterator = self._read_xls_book(book)
            headers = next(iterator)  # pylint: disable=stop-iteration-return
            missing_headers = EXPECTED_COLUMNS - set(headers)
            if missing_headers:
                raise ValidationError(
                    _(
                        "The xlsx file doesn't contains columns %(missing_headers)s",
                        missing_headers=missing_headers,
                    )
                )
            for values in iterator:
                row = dict(zip(headers, values, strict=False))
                windows = []
                days_by_start_end = defaultdict(list)
                for start, end in (
                    ("mon_start1", "mon_end1"),
                    ("mon_start2", "mon_end2"),
                    ("tue_start1", "tue_end1"),
                    ("tue_start2", "tue_end2"),
                    ("wed_start1", "wed_end1"),
                    ("wed_start2", "wed_end2"),
                    ("thu_start1", "thu_end1"),
                    ("thu_start2", "thu_end2"),
                    ("fri_start1", "fri_end1"),
                    ("fri_start2", "fri_end2"),
                ):
                    day = None
                    if start.startswith("mon"):
                        day = self.monday
                    elif start.startswith("tue"):
                        day = self.tuesday
                    elif start.startswith("wed"):
                        day = self.wednesday
                    elif start.startswith("thu"):
                        day = self.thursday
                    elif start.startswith("fri"):
                        day = self.friday
                    days_by_start_end[(row[start], row[end])].append(day.id)
                for start_end, day_ids in days_by_start_end.items():
                    start = start_end[0]
                    end = start_end[1]
                    if start and end:
                        windows.append(Window(day_ids, start, end))
                yield TopCustomer(
                    ref=row["code"],
                    windows=windows,
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
        values = {"toursolver_delivery_window_ids": [(5, None, None)]}
        window_values = [
            (
                0,
                0,
                self._to_delivery_window_values(
                    window.start,
                    window.end,
                    window.day_ids,
                ),
            )
            for window in top_customer.windows
        ]
        values = {"toursolver_delivery_window_ids": window_values}
        partners.write(values)
        _logger.info("%s updated", top_customer.ref)

    def _to_delivery_window_values(self, start, end, day_ids):
        return {
            "time_window_start": self._dt_to_float(start),
            "time_window_end": self._dt_to_float(end),
            "time_window_weekday_ids": [(6, 0, day_ids)],
        }

    def _dt_to_float(self, dt):
        if isinstance(dt, str):
            hour, minute = map(int, dt.split(":"))
        else:
            hour, minute = dt.hour, dt.minute
        return hour + minute / 60.0

    def _read_xls_book(self, book):
        sheet = book.sheet_by_index(0)
        # emulate Sheet.get_rows for pre-0.9.4
        for row in list(map(sheet.row, range(sheet.nrows))):
            values = []
            for cell in row:
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(str(cell.value) if is_float else str(int(cell.value)))
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    dt = xlrd.xldate.xldate_as_datetime(cell.value, book.datemode)
                    values.append(dt)
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append("True" if cell.value else "False")
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    error = xlrd.error_text_from_code.get(
                        cell.value, f"unknown error code {cell.value}"
                    )
                    raise ValueError(
                        _(
                            "Error cell found while reading XLS/XLSX file: %(error)s",
                            error=error,
                        )
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values
