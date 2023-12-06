# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.tools import mute_logger

from odoo.addons.alc_price_cache.tests.common import TestPrices

from .common import TestImport


class TestPricelistItemFlow(TestPrices, TestImport):
    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.utils")
    def test_no_delay_import_change_min_qty(self):
        """Items with minimum quantities and without belong to two different categories.

        changing one without must ensure we clean it from the standard cache.
        """
        # given
        tmpl = self.product_1.product_tmpl_id
        vals = self._get_pricelist_vals("DPL", [], is_discount=True)
        discount_pricelist = self.model_pl_nodelay.create(vals)
        role = discount_pricelist.discount_role_name
        self.assertFalse(self.product_1.price_cache)
        vals_item_min_qty = self._get_item_vals(
            discount_pricelist,
            min_quantity=0,
            applied_on="1_product",
            product_tmpl_id=tmpl.id,
        )
        item = self.model_pl_item_nodelay.create(vals_item_min_qty)

        external_id_template = self._create_external_id(tmpl)
        external_id_item = self._create_external_id(item)

        # the import is based on the label and not on the key, but it can be overriden
        # which is done in specific_product, of course
        # if the label is wrong, import does not really happen and contains a message
        field_base = item._fields["base"]
        label_price = next(s[1] for s in field_base.selection if s[0] == "list_price")

        fields = [
            "id",
            "applied_on",
            "base",
            "compute_price",
            "min_quantity",
            "percent_price",
            "product_tmpl_id/id",
        ]
        data = [
            [
                external_id_item,
                "Product",
                label_price,
                "Discount",
                "20",
                "10",
                external_id_template,
            ]
        ]
        # when
        self.model_pl_item_nodelay.load(fields, data)
        # then
        price_cache = self.product_1.price_cache[role]
        expected_cache_element = {
            "discount": 10.0,
            "date_start": None,
            "id": item.id,
            "date_end": None,
            "min_quantity": 20,
        }
        self.assertEqual(len(price_cache), 1)
        for (
            field,
            value,
        ) in expected_cache_element.items():  # allow other modules to add keys in cache
            self.assertEqual(price_cache[0][field], value)
