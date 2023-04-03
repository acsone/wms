# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    addons_to_uninstall = [
        "alc_delivery_rounds_allatonce_assignment",
        "alc_delivery_rounds_partner_geolocalize",
        "alce_stock_barcode_easy_operation",  # replaced by STD
        "web_decimal_numpad_dot",
        "alc_stock_picking_batch_delivery_rounds",  # replaced by alc_stock_release_channel_picking_batch_creation
    ]
    for addon in addons_to_uninstall:
        _logger.info("uninstall %s", addon)
        cr.execute(
            "update ir_module_module set state = 'to remove' where name = %s",
            (addon,),
        )
