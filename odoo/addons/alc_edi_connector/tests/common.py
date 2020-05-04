# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import mock
from odoo import fields
from odoo.addons.component.tests.common import SavepointComponentCase
from odoo.addons.queue_job.tests.common import JobMixin


class AlcEdiConnectorCase(SavepointComponentCase, JobMixin):
    @classmethod
    def setUpClass(cls):
        super(AlcEdiConnectorCase, cls).setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.edi_backend = cls.env["edi.backend"].create(
            {
                "name": "EDI test",
                "hostname": "localhost",
                "password": "password",
                "username": "username",
                "edi_export_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.exporter",
                            "export_filename": "PO{id}_{date}-{time}.xml",
                        },
                    )
                ],
                "edi_import_task_def_ids": [
                    (
                        0,
                        0,
                        {
                            "kind": "ubl.order.response.importer",
                            "file_matcher_pattern": "PO.*.xml$",
                        },
                    )
                ],
            }
        )
        cls.supplier = cls.env.ref("base.res_partner_12")
        cls.supplier.write(
            {
                "vat": "BE0477472701",
                "use_edi_connector": True,
                "edi_backend_id": cls.edi_backend.id,
                "purchase_requires_second_approval": "always",
            }
        )
        cls.supplier_no_edi = cls.supplier.copy(
            {"use_edi_connector": False, "edi_backend_id": False}
        )
        cls.env.user.company_id.partner_id.vat = "BE0421801233"
        cls.currency_euro = cls.env.ref("base.EUR")
        cls.currency_usd = cls.env.ref("base.USD")
        cls.product_1 = cls.env["product.product"].create(
            {
                "name": "Product 1",
                "seller_ids": [(0, 0, {"name": cls.supplier.id, "product_code": "P1"})],
            }
        )
        cls.product_2 = cls.env["product.product"].create(
            {
                "name": "Product 2",
                "seller_ids": [(0, 0, {"name": cls.supplier.id, "product_code": "P2"})],
            }
        )
        cls.purchase_order = cls.env["purchase.order"].create(
            {
                "partner_id": cls.supplier.id,
                "date_order": fields.Datetime.now(),
                "date_planned": fields.Datetime.now(),
                "currency_id": cls.currency_euro.id,
            }
        )
        cls.line1 = cls.purchase_order.order_line.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_1.id,
                "name": cls.product_2.name,
                "date_planned": fields.Datetime.now(),
                "product_qty": 10,
                "product_uom": cls.env.ref("product.product_uom_unit").id,
                "price_unit": 15,
            }
        )
        cls.line2 = cls.purchase_order.order_line.create(
            {
                "order_id": cls.purchase_order.id,
                "product_id": cls.product_2.id,
                "name": cls.product_2.name,
                "date_planned": fields.Datetime.now(),
                "product_qty": 5,
                "product_uom": cls.env.ref("product.product_uom_unit").id,
                "price_unit": 25,
            }
        )
        cls.purchase_order.button_approve()

    def setUp(self):
        super(AlcEdiConnectorCase, self).setUp()
        JobMixin.setUp(self)
        with self.edi_backend.work_on("edi.backend") as work:
            sftp_adapter = work.component(usage="sftp.backend.adapter")
        sftp_push_patcher = mock.patch.object(sftp_adapter.__class__, "push")
        sftp_pull_patcher = mock.patch.object(sftp_adapter.__class__, "pull")
        self.mocked_sftp_push = sftp_push_patcher.start()
        self.mocked_sftp_pull = sftp_pull_patcher.start()

        @self.addCleanup
        def stop_mock():
            sftp_push_patcher.stop()
            sftp_pull_patcher.stop()

    def _get_attachments(self, model_instance):
        return self.env["ir.attachment"].search(
            [
                ("res_model", "=", model_instance._name),
                ("res_id", "=", model_instance.id),
            ]
        )
