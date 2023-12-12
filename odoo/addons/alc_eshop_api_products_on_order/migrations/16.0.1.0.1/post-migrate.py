# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Remove old and duplicate mail template
    old_template = env.ref(
        "alc_eshop_product_on_order.sale_order_request_backorder_cancellation",
        raise_if_not_found=False,
    )
    if old_template:
        old_template.unlink()
    openupgrade.load_data(
        env.cr, "alc_eshop_api_products_on_order", "data/mail_template.xml", mode="init"
    )
