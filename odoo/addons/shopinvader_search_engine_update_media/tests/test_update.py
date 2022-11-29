# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader_search_engine_update_product.tests.common import (
    TestProductUpdate,
)


class TestProductExportFlow(TestProductUpdate):
    def test_flow(self):
        backend = self.env.ref("storage_backend.default_storage_backend")
        file = self.env["storage.file"].create(
            {"name": "file", "backend_id": backend.id}
        )
        media = self.env["storage.media"].create({"name": "media", "file_id": file.id})

        # given
        vals = {"media_id": media.id, "product_tmpl_id": self.product_template.id}
        # when
        rel = self.env["product.media.relation"].create(vals)
        # then
        self.assertEqual(self.binding.to_update, "true")

        # given
        self.binding.to_update = "false"
        # when
        rel.write({"sequence": 1})
        # then
        self.assertEqual(self.binding.to_update, "true")

        # given
        self.binding.to_update = "false"
        # when
        rel.unlink()
        # then
        self.assertEqual(self.binding.to_update, "true")
