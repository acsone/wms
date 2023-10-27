# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.alc_product_flattened_data.tests.common import TestProductFlattenedData
from odoo.addons.fastapi.tests.common import FastAPITransactionCase

from ..routers import brands_router, catalog_router


class TestBrandsService(FastAPITransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = brands_router

        cls.partner = cls.env["res.partner"].create({"name": "P"})
        cls.brand_1 = cls.env["product.brand"].create({"name": "numbah 1"})
        cls.brand_2 = cls.env["product.brand"].create({"name": "numéro 2"})


class TestCatalogService(FastAPITransactionCase, TestProductFlattenedData):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_fastapi_router = catalog_router

        vals_partner = {"name": "P", "partner_type": "veterinary"}
        cls.partner = cls.env["res.partner"].create(vals_partner)
