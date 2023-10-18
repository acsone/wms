# Copyright 2021-2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.fields import Command

from odoo.addons.stock_storage_type.tests.common import TestStorageTypeCommon


class AlcAbcClassificationStorageTypeCommon(TestStorageTypeCommon):
    @classmethod
    def _create_profile(cls):
        level_obj = cls.env["abc.classification.level"]
        level_a = level_obj.create(
            {
                "name": "a",
                "percentage": 75,
                "percentage_products": 10,
            }
        )
        level_b = level_obj.create(
            {
                "name": "b",
                "percentage": 15,
                "percentage_products": 20,
            }
        )
        level_c = level_obj.create(
            {
                "name": "c",
                "percentage": 10,
                "percentage_products": 70,
            }
        )
        return cls.env["abc.classification.profile"].create(
            {
                "name": "Alternative profile",
                "profile_type": "sale_stock",
                "warehouse_id": cls.env.ref("stock.warehouse0").id,
                "period": 730,
                "level_ids": [Command.set((level_a | level_b | level_c).ids)],
            }
        )

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product_obj = cls.env["product.product"]
        cls.cardboxes_type = cls.env.ref(
            "stock_storage_type.package_storage_type_cardboxes"
        )
        cls.pallet_type = cls.env.ref("stock_storage_type.package_storage_type_pallets")
        cls.product_alc_1 = cls.product_obj.create(
            {
                "name": "Test Product (Alc 1)",
                "type": "product",
            }
        )
        cls.route_mto = cls.env.ref("stock.route_warehouse0_mto")
        cls.route_mto.active = True
        cls.product_alc_mto = cls.product_obj.create(
            {
                "name": "Test Product (Alc MTO)",
                "type": "product",
                "route_ids": [Command.set(cls.route_mto.ids)],
            }
        )

        # Load the profile and its levels.
        cls.stock_profile = cls.env.ref(
            "product_abc_classification_sale_stock."
            "abc_classification_profile_sale_stock"
        )
        cls.level_A = cls.env.ref(
            "product_abc_classification_sale_stock.abc_classification_level_a"
        )
        cls.level_B = cls.env.ref(
            "product_abc_classification_sale_stock.abc_classification_level_b"
        )
        cls.level_C = cls.env.ref(
            "product_abc_classification_sale_stock.abc_classification_level_c"
        )

        cls.profile_2 = cls._create_profile()
