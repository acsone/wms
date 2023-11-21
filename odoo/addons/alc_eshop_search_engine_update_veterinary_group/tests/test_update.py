# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import Command

from odoo.addons.shopinvader_search_engine_update.tests.common import (
    TestProductBindingUpdateBase,
)


class TestProductExportFlow(TestProductBindingUpdateBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, es_security_no_autosync=True
            )
        )
        cls.product_template = cls.product.product_tmpl_id

    def test_0(self):
        # case create
        self.assertEqual(self.product_binding.state, "done")
        vals = {
            "name": "Test VT Group",
            "product_template_ids": [Command.set(self.product_template.ids)],
        }
        vt_group = self.env["veterinary.group"].create(vals)
        self.assertEqual(self.product_binding.state, "to_recompute")
        # Case write
        # when just modifying the partner does not mark products to update
        self.product_binding.state = "done"
        partner = self.env["res.partner"].create({"name": "P"})
        vt_group.write({"partner_ids": [Command.set(partner.ids)]})
        self.assertEqual(self.product_binding.state, "done")
        # Case update 2
        # if we removed the product, it is updated
        vt_group.product_template_ids = False
        self.assertEqual(self.product_binding.state, "to_recompute")

        # we add it back in to test unlink
        vt_group.product_template_ids = self.product_template
        self.product_binding.state = "done"
        vt_group.unlink()
        self.assertEqual(self.product_binding.state, "to_recompute")
