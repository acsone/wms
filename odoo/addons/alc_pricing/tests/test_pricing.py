# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from freezegun import freeze_time

from odoo.tools import mute_logger

from .common import TestPricing


class TestPricingFlow(TestPricing):
    @freeze_time("2022-01-01 12:00:00")
    @mute_logger("odoo.addons.queue_job.models.base")
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
    @mute_logger("odoo.addons.queue_job.models.base")
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
