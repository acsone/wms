# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.addons.stock_move_zone_location_source.tests.common import (
    ZoneLocationSourceCommon,
)


class PickingParcelsItemsCommon(ZoneLocationSourceCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        test_carrier_product = cls.env["product.product"].create(
            {
                "name": "Test carrier product",
                "type": "service",
            }
        )
        cls.test_carrier = cls.env["delivery.carrier"].create(
            {
                "name": "Test carrier",
                "delivery_type": "fixed",
                "product_id": test_carrier_product.id,
            }
        )
        cls.package_type = cls.env["stock.package.type"].create(
            {
                "name": "package type",
                "number_of_parcels": 7,
            }
        )

        cls.pharma_type.set_delivery_package_type_on_put_in_pack = True
        cls.food_type.set_delivery_package_type_on_put_in_pack = True
        cls.warehouse.pick_type_id.set_delivery_package_type_on_put_in_pack = True

    def _put_in_pack(self, picking):
        picking.group_id.carrier_id = self.test_carrier

        pack_action = picking.action_put_in_pack()
        pack_action_ctx = pack_action["context"]
        pack_action_model = pack_action["res_model"]
        # We make sure the correct action was returned
        self.assertEqual(pack_action_model, "choose.delivery.package")
        # check there is no package yet for the picking
        self.assertEqual(len(picking.package_ids), 0)
        # We instanciate the wizard with the context of the action
        pack_wiz = (
            self.env["choose.delivery.package"]
            .with_context(**pack_action_ctx)
            .create({})
        )
        # set the package type
        pack_wiz.delivery_package_type_id = self.package_type
        pack_wiz.action_put_in_pack()

    def _get_jsonb(self, json_value):
        # As integer keys have been converted to string.
        final = {}
        for key, value in json_value.items():
            final[int(key)] = value
        return final
