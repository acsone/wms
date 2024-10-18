# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.shopinvader_search_engine.tests.common import TestProductBindingBase


class TestSeBindingSanitizer(TestProductBindingBase):

    def test_mark_to_recompute_failed_binding(self):
        self.product_binding.state = "recompute_error"
        self.env["se.binding"]._mark_to_recompute_failed_binding()
        self.assertEqual(self.product_binding.state, "to_recompute")

    def test_ensure_unpublish_inactives(self):
        self.product.active = False
        self.product_binding.state = "done"
        self.env["se.binding"]._ensure_unpublish_inactives()
        self.assertEqual(self.product_binding.state, "to_delete")

    def test_cron_sanitizer(self):
        binding_class = self.env["se.binding"].__class__
        with patch.object(
            binding_class, "_mark_to_recompute_failed_binding"
        ) as mark_to_recompute_failed_binding:
            with patch.object(
                binding_class, "_ensure_unpublish_inactives"
            ) as ensure_unpublish_inactives:
                self.env["se.binding"]._cron_sanitizer()
                mark_to_recompute_failed_binding.assert_called_once()
                ensure_unpublish_inactives.assert_called_once()
