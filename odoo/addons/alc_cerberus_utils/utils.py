# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import dateutil
import pytz


def odoo_dt_to_dt_utc(value_dt):
    if not value_dt:
        return None
    return pytz.utc.localize(value_dt, is_dst=False)


def isoformat_str_dt_to_dt_utc(value_str):
    dt = dateutil.parser.parse(value_str)
    return dt.astimezone(pytz.timezone("UTC"))
