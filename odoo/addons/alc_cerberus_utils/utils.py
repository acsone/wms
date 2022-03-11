# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import dateutil
import pytz

from odoo import fields


def odoo_str_dt_to_dt_utc(value_str):
    if not value_str:
        return None
    dt = fields.Datetime.from_string(value_str)
    return pytz.utc.localize(dt, is_dst=False)


def isoformat_str_dt_to_dt_utc(value_str):
    dt = dateutil.parser.parse(value_str)
    return dt.astimezone(pytz.timezone("UTC"))
