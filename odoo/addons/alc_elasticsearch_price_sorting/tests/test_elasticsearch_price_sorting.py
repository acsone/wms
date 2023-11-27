# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from vcr_unittest import VCRTestCase

from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from odoo.addons.queue_job.tests.common import trap_jobs


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
        self.backend.create_or_update_net_price_sort_script()

    def test_1(self):
        self.backend.create_or_update_current_price_pipeline_script()

    def test_02(self):
        with trap_jobs() as trap:
            self.backend.cron_execute_pipeline_set_current_price()
            trap.assert_jobs_count(1)
            self.assertEqual(
                trap.enqueued_jobs[0].method_name, "_check_es_task_completion"
            )
            trap.perform_enqueued_jobs()

    @mute_logger(
        "odoo.addons.alc_connector_search_engine_put_script_mixin.models.se_backend"
    )
    def test_03(self):
        self.backend.es_password = "wrong_password"
        with self.assertRaises(UserError, msg="HTTPSConnection"):
            self.backend.create_or_update_net_price_sort_script()
