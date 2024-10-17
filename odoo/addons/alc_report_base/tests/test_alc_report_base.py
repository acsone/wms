# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.tests.common import TransactionCase


class TestAlcReportBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        external_layout = cls.env.ref("alc_report_base.external_layout_alcyon")
        cls.company = cls.env.user.company_id
        cls.company.external_report_layout_id = external_layout
        cls.company.street = "My street"
        cls.company.zip = "123456789"
        cls.company.city = "My city"
        cls.company.country_id = cls.env.ref("base.be")
        cls.company.phone = "+32 987654"
        cls.company.partner_id.fax = "+32 654987"
        cls.company.email = "brol@company.com"
        cls.company.order_phone = "+32 123456"
        cls.company.order_fax = "+32 456123"
        cls.company.vat = "BE 0835.207.216"
        cls.company.logo = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAALklEQVR42u3OMQEAAAgDoNk/jgE1xh5IwNzmUjQCAgICAgICAgICAgICAgLtwAONFFZBP1VacgAAAABJRU5ErkJggg=="

        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()

        # pylint: disable=import-outside-toplevel
        from .models import TestModel

        cls.loader.update_registry([TestModel])

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    def test_basic(self):
        # Create report action
        vals = {
            "name": "test_report",
            "model": "test.model",
            "report_name": "web.external_layout",
            "report_file": "web.external_layout",
        }
        report_action = self.env["ir.actions.report"].create(vals)

        obj = self.env["test.model"].create([{}])
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", obj.id),
                ("res_model", "=", obj._name),
            ]
        )
        self.assertTrue(not attachments)
        obj.print_and_attach_report(report_action, "012 0234 23")
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", obj.id),
                ("res_model", "=", obj._name),
            ]
        )
        self.assertFalse(not attachments)
