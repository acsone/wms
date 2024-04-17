from unittest import mock

from odoo.modules.module import get_module_resource
from odoo.tests import common


class TestReportQWebPdfBatch(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context, tracking_disable=True, force_report_rendering=True
            )
        )
        cls.IrActionsReport = cls.env["ir.actions.report"]
        cls.report_vals = {
            "name": "Test Report",
            "model": "ir.actions.report",
            "report_name": "Test Report",
        }
        cls.report_pdf_view = cls.env["ir.ui.view"].create(
            {
                "name": "Test",
                "type": "qweb",
                "arch": """<t t-name="alc_report_qweb_pdf_batch.test">
                 <t t-call="web.html_container">
                    <t t-foreach="docs" t-as="o">
                        <h1><t t-esc="o.name"/></h1>
                        <div>Test</div>
                    </t>
                </t>
            </t>""",
            }
        )
        cls.report_pdf_imd = (
            cls.env["ir.model.data"]
            .sudo()
            .create(
                {
                    "name": "test_pdf",
                    "module": "alc_report_qweb_pdf_batch",
                    "model": "ir.ui.view",
                    "res_id": cls.report_pdf_view.id,
                }
            )
        )
        cls.report = cls.IrActionsReport.create(
            {
                "name": "Test",
                "report_type": "qweb-pdf",
                "model": "res.partner",
                "report_name": "alc_report_qweb_pdf_batch.test_pdf",
            }
        )
        cls.partners = cls.env["res.partner"]
        for n in range(5):
            cls.partners += cls.env["res.partner"].create({"name": f"Test {n}"})
        cls.env["ir.config_parameter"].sudo().set_param(
            "alc_report_qweb_pdf_batch.enable_render_qweb_pdf_batch", True
        )

        # We mock the wkhtmltopdf command to avoid calling it in the tests
        cls.wkhtmltopdf_patcher = mock.patch.object(
            type(cls.report), "_run_wkhtmltopdf"
        )

        dummy_pdf = get_module_resource(
            "alc_report_qweb_pdf_batch", "tests", "dummy.pdf"
        )
        with open(dummy_pdf, "rb") as f:
            cls.dummy_pdf_content = f.read()
        patched = cls.wkhtmltopdf_patcher.start()
        patched.return_value = cls.dummy_pdf_content
        # at cleanup, we stop the patcher
        cls.addClassCleanup(cls.wkhtmltopdf_patcher.stop)

    @classmethod
    def _set_pdf_batch_size(cls, size):
        cls.env["ir.config_parameter"].sudo().set_param(
            "alc_report_qweb_pdf_batch.render_qweb_pdf_batch_size", size
        )

    def new_record(self):
        return self.IrActionsReport.create(self.report_vals)

    def test_render_qweb_multi_batch_pdf(self):
        """It should print the report, only if it is printable."""
        self._set_pdf_batch_size(2)
        with mock.patch.object(type(self.report), "_merge_pdfs") as mock_merge_pdfs:
            res = self.report._render_qweb_pdf(
                self.report.report_name, self.partners.ids
            )
            self.assertTrue(mock_merge_pdfs.called)
            # [1, 2] and [3, 4, 5]
            self.assertEqual(len(mock_merge_pdfs.call_args[0][0]), 2)
            self.assertTrue(res[0], "pdf")

    def test_render_qweb_pdf(self):
        self._set_pdf_batch_size(4)
        with mock.patch.object(type(self.report), "_merge_pdfs") as mock_merge_pdfs:
            res = self.report._render_qweb_pdf(
                self.report.report_name, self.partners.ids
            )
            # since all the 5 records are in the same batch, we should not call merge_pdfs
            self.assertFalse(mock_merge_pdfs.called)
            self.assertTrue(res[0], "pdf")

    def test_render_single_qweb_pdf(self):
        self._set_pdf_batch_size(4)
        with mock.patch.object(type(self.report), "_merge_pdfs") as mock_merge_pdfs:
            res = self.report._render_qweb_pdf(
                self.report.report_name, self.partners[0].ids
            )
            # since we have only one record, we should not call merge_pdfs
            self.assertFalse(mock_merge_pdfs.called)
            self.assertTrue(res[0], "pdf")

    def test_batches(self):
        # we test that we never have a batch with a single element
        batches = list(self.report._split_batches(list(range(5)), batch_size=2))
        # we must have 2 batches. One with 2 elements and one with 3 elements
        self.assertEqual(len(batches), 2)
        self.assertListEqual(batches[0], [0, 1])
        self.assertListEqual(batches[1], [2, 3, 4])

        batches = list(self.report._split_batches(list(range(5)), batch_size=4))
        self.assertEqual(len(batches), 1)
        self.assertListEqual(batches[0], [0, 1, 2, 3, 4])

        batches = list(self.report._split_batches(list(range(4)), batch_size=4))
        self.assertEqual(len(batches), 1)
        self.assertListEqual(batches[0], [0, 1, 2, 3])

        batches = list(self.report._split_batches(list(range(4)), batch_size=10))
        self.assertEqual(len(batches), 1)
        self.assertListEqual(batches[0], [0, 1, 2, 3])

        batches = list(self.report._split_batches([1], batch_size=10))
        self.assertEqual(len(batches), 1)
