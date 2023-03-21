# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _rename_daily_sale(env):
    # Rename only configuration model as the data one is recreated at each time

    # First rename model
    models = [
        ("alc.product.average.daily.sale.config", "stock.average.daily.sale.config")
    ]
    openupgrade.rename_models(env.cr, models)

    # Then, rename table
    tables = [
        ("alc_product_average_daily_sale_config", "stock_average_daily_sale_config")
    ]
    openupgrade.rename_tables(env.cr, tables)

    # Then, rename fields that have been adapted
    fields = [
        (
            "purchase.order.line",
            "purchase_order_line",
            "stddev_exclude_factor",
            "standard_deviation_exclude_factor",
        )
    ]
    openupgrade.rename_fields(env, fields)


@openupgrade.migrate()
def migrate(env, version):
    _rename_daily_sale(env)
