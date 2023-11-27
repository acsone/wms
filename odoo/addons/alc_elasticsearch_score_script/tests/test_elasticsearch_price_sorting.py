# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from vcr_unittest import VCRTestCase

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger


class TestElasticsearchPriceSorting(VCRTestCase, TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env.ref("alc_search_engine_backend.elasticsearch_backend")
        cls.backend.write(
            {
                "es_server_host": "https://index.test.alcyon.acsone.eu/",
                "es_user": "odoo",
                "es_password": "fake_password",
                "auth_type": "http",
            }
        )
        cls.se_config = cls.env["se.index.config"].create(
            {"name": "my_config", "body": {"mappings": {}}}
        )
        cls.product_index = cls.env["se.index"].create(
            {
                "name": "product",
                "backend_id": cls.backend.id,
                "model_id": cls.env.ref("product.model_product_product").id,
                "serializer_type": "shopinvader_product_exports",
                "config_id": cls.se_config.id,
            }
        )

    def test_0(self):
        self.backend.create_or_update_score_on_position_script()

    @mute_logger(
        "odoo.addons.alc_connector_search_engine_put_script_mixin.models.se_backend"
    )
    def test_02(self):
        self.backend.es_password = "wrong_password"
        with self.assertRaises(UserError, msg="HTTPSConnection"):
            self.backend.create_or_update_score_on_position_script()
