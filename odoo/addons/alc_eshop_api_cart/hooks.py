# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    """This hook is executed before installing the module."""
    # rename xml_id
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_eshop_sale_cart_confirm.sale_order_notify_note",
                "alc_eshop_api_cart.sale_order_notify_note",
            ),
        ],
    )
