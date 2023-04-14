# Copyright 2018 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo.fields import Command
from odoo.tests.common import TransactionCase


class TestSaleOrderExceptionCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.partner = cls.env.ref("base.res_partner_1")
        cls.prod1 = cls.env["product.product"].create(
            {
                "name": "Corner Desk Right Sit",
                "type": "product",
            }
        )
        cls.so1_vals = {
            "partner_id": cls.partner.id,
            "date_order": "2018-01-29",
            "client_order_ref": "whatever the client want",
            "order_line": [
                Command.create(
                    {
                        "sequence": 1,
                        "name": cls.prod1.name,
                        "product_id": cls.prod1.id,
                        "product_uom_qty": 20,
                    },
                )
            ],
        }

    @classmethod
    def get_module_exception_ids(cls, module=None):
        module = module if module else cls.current_module
        exceptions = cls.env["ir.model.data"].search(
            [("module", "=", module), ("model", "=", "exception.rule")]
        )
        return exceptions.mapped("res_id")

    @classmethod
    def activate_module_exceptions_only(cls):
        exceptions = cls.env["exception.rule"].search(
            [("id", "not in", cls.current_exception_ids)]
        )
        exceptions.write({"active": False})
        exceptions = cls.env["exception.rule"].browse(cls.current_exception_ids)
        exceptions.write({"active": True})
