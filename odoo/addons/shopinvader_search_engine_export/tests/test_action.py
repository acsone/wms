# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import unittest

from .common import TestProductExport


@unittest.skip("Mock ES")
class TestProductExportFlow(TestProductExport):
    def test_template(self):
        self.product_template.shopinvader_manual_export()

    def test_product(self):
        self.product.shopinvader_manual_export()
