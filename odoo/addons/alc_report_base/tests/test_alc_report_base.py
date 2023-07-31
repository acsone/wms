# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tests.common import TransactionCase


class TestAlcReportBase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.company = cls.env.user.company_id
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

    def test_basic(self):
        class TestModel(models.Model):
            _name = "test.model"
            _inherit = ["report.async"]

            def get_report_name(self):
                return "Test report"

        model_name = TestModel._name
        self.registry.models[model_name] = TestModel._build_model(
            self.registry, self.cr
        )
        self.registry.setup_models(self.cr)
        self.registry.init_models(
            self.cr, [model_name], {"module": "test"}, install=True
        )

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
        self.assertTrue(len(attachments) == 0)
        obj.print_and_attach_report(report_action, "012 0234 23")
        attachments = self.env["ir.attachment"].search(
            [
                ("res_id", "=", obj.id),
                ("res_model", "=", obj._name),
            ]
        )
        self.assertFalse(len(attachments) == 0)
