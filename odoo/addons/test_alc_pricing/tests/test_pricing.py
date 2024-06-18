# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.tools import mute_logger

from .common import TestPricing


class TestPricingFlow(TestPricing):
    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_so_1(self):
        # when
        line_1 = self._new_sale_line(self.so_1, self.product_1)

        # then: supplier discount is not applied since we get an exclusive discount
        self.assertEqual(line_1.discount2, 0)
        self.assertEqual(line_1.discount3, 10)

        # when
        line_2 = self._new_sale_line(self.so_1, self.product_2)

        # then: both discounts have a value
        self.assertEqual(line_2.discount2, 20)
        self.assertEqual(line_2.discount3, 10)

        # when
        line_3 = self._new_sale_line(self.so_1, self.product_3)

        # then: no discounts
        self.assertEqual(line_3.discount2, 0)
        self.assertEqual(line_3.discount3, 0)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_so_2(self):
        # when
        line_1 = self._new_sale_line(self.so_2, self.product_1)

        # then: both discounts have a value
        self.assertEqual(line_1.discount2, 20)
        self.assertEqual(line_1.discount3, 10)

        # when
        line_2 = self._new_sale_line(self.so_2, self.product_2)

        # then: supplier discount is not applied since we get an exclusive discount
        self.assertEqual(line_2.discount2, 0)
        self.assertEqual(line_2.discount3, 10)

        # given
        vals_sinfo_3 = self.get_supplierinfo_vals(self.product_3, discount_sale=20)
        vals_sinfo_3.pop("price")
        self.supplierinfo_model.create(vals_sinfo_3)

        # when
        line_3 = self._new_sale_line(self.so_2, self.product_3)

        # then: supplier discount, no alcyon discount
        self.assertEqual(line_3.discount2, 20)
        self.assertEqual(line_3.discount3, 0)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_multiple_discount_pricelists(self):
        vals = {"discount_pricelist_ids": [(4, self.dpl_1.id), (4, self.dpl_2.id)]}
        self.customer_1.write(vals)
        so = self.env["sale.order"].create({"partner_id": self.customer_1.id})

        # when
        line_1 = self._new_sale_line(so, self.product_1)

        # then: we got the best discount, an exclusive one from dpl_1
        self.assertEqual(line_1.discount2, 0)
        self.assertEqual(line_1.discount3, 50)
        self.assertEqual(line_1.discount_item_id, self.item_1_1)

        # when
        line_2 = self._new_sale_line(so, self.product_2)

        # then: we got the best discount, a non-exclusive one from dpl_2
        self.assertEqual(line_2.discount2, 20)
        self.assertEqual(line_2.discount3, 50)
        self.assertEqual(line_2.discount_item_id, self.item_2_2)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_discount_priority(self):
        self.customer_1.write({"discount_pricelist_ids": [(4, self.dpl_1.id)]})
        vals_item_global = self._get_item_vals(
            pricelist=self.dpl_1,
            applied_on="3_global",
            percent_price=90,
            exclusive=False,
        )
        item_global = self.model_pl_item_nodelay.create(vals_item_global)
        so = self.env["sale.order"].create({"partner_id": self.customer_1.id})

        # when
        line_1 = self._new_sale_line(so, self.product_1)

        # then: the global item was ignored because there is a more precise one
        self.assertEqual(line_1.discount2, 0)
        self.assertEqual(line_1.discount3, 50)
        self.assertEqual(line_1.discount_item_id, self.item_1_1)

        # when
        line_product_3 = self._new_sale_line(so, self.product_3)

        # then: the global item was applied
        self.assertEqual(line_product_3.discount3, 90)
        self.assertEqual(line_product_3.discount_item_id, item_global)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_discount_based_on_cost(self):
        """For a percentage discount item, basing on standard_price has no effect."""
        # given: percentage item based on standard_price (cost), differing from price
        self.product_3.standard_price = 5
        vals = self._get_item_vals(
            pricelist=self.customer_1.discount_pricelist_ids[0],
            applied_on="0_product_variant",
            product_id=self.product_3.id,
            compute_price="percentage",
            base="standard_price",
            percent_price=50,
        )
        self.model_pl_item_nodelay.create(vals)

        # when
        line_1 = self._new_sale_line(self.so_1, self.product_3)

        # then: the base does not really matter, only the percentage is taken into account
        self.assertEqual(line_1.discount3, 50)

    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.delay")
    def test_base_price_based_on_cost(self):
        self.product_3.standard_price = 5
        vals = self._get_item_vals(
            pricelist=self.customer_1.property_product_pricelist,
            applied_on="0_product_variant",
            product_id=self.product_3.id,
            compute_price="formula",
            base="standard_price",
            price_discount=-4,
        )
        self.model_pl_item_nodelay.create(vals)

        # when
        line_1 = self._new_sale_line(self.so_1, self.product_3)

        self.assertEqual(line_1.price_unit, 5.2)
        self.assertEqual(
            self.product_3.price_cache[self.pricelist_base.role_name][0]["price"], 5.2
        )
