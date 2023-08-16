# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopfloor.tests.test_cluster_picking_base import (
    ClusterPickingCommonCase,
)


class TestPrintProductLotLabelCommon(ClusterPickingCommonCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Printer = cls.env["printing.printer"].sudo()
        Printer.search([]).unlink()
        printer_server = (
            cls.env["printing.server"]
            .sudo()
            .create({"name": "Localhost", "address": "no_printing", "port": "1234"})
        )

        cls.printer1 = Printer.create(
            {
                "name": "Test printer 1",
                "system_name": "test_printer_1",
                "model": "toshiba",
                "server_id": printer_server.id,
            }
        )

        cls.printer2 = Printer.create(
            {
                "name": "Test printer 2",
                "system_name": "test_printer_2",
                "model": "zebra",
                "server_id": printer_server.id,
            }
        )
