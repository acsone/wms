# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import mute_logger

from odoo.addons.alc_documents.tests.common import TestAlcDocuments
from odoo.addons.alc_product_flattened_data.tests.common import TestProductFlattenedData


class TestAlcDocumentsPrices(TestAlcDocuments, TestProductFlattenedData):
    @classmethod
    @mute_logger("odoo.addons.queue_job.utils")
    def setUpClass(cls):
        super().setUpClass()
        cat_web = cls.env.ref("alc_product_shop_category.master")
        all_products = cls.env["product.product"].search([])
        all_products.categ_ids = cat_web
        all_products.web_published = True
        cls.env["alc.product.flattened.data"].refresh_view()
