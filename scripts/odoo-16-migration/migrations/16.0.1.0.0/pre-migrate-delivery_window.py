# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_delivery_window(cr):
    openupgrade.rename_columns(
        cr,
        {
            "alc_delivery_window": [
                ("start", "time_window_start"),
                ("end", "time_window_end"),
            ],
            "alc_delivery_week_day_alc_delivery_window_rel": [
                ("alc_delivery_window_id", "toursolver_delivery_window_id"),
                ("alc_delivery_week_day_id", "time_weekday_id"),
            ],
        },
    )
    openupgrade.rename_tables(
        cr,
        [
            ("alc_delivery_week_day", "time_weekday"),
            ("alc_delivery_window", "toursolver_delivery_window"),
            (
                "alc_delivery_week_day_alc_delivery_window_rel",
                "time_weekday_toursolver_delivery_window_rel",
            ),
        ],
    )
    openupgrade.rename_models(cr, [("alc.delivery.week.day", "time.weekday")])
    # change xmlid model
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    openupgrade.rename_xmlids(
        cr,
        [
            (
                f"alc_partner_delivery_window.alc_delivery_weed_day_{day}",
                f"base_time_window.time_weekday_{day}",
            )
            for day in days
        ],
    )


def migrate(cr, version):
    _rename_delivery_window(cr)
