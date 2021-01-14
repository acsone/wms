# -*- coding: utf-8 -*-
import mock

from odoo.tools import mute_logger

from .. import constants
from ..tools.domain_interface import Parameters
from ..tools.domain_print import Print
from .zetes_test_classes import ZetesTest


class TestPrint(ZetesTest):
    @mute_logger(
        "odoo.addons.base_report_to_printer.models.printing_server",
        "odoo.addons.specific_zetes.tools.domain_print",
        "odoo.addons.specific_print.models.stock",
    )
    def test_requ_print(self):
        """
        :return:
        """
        printer = self.env["printing.printer"]
        printer.search([]).unlink()

        logger = self.env["zetes.logger"]
        logger.search([]).unlink()

        printer_server = self.env["printing.server"].create(
            {"name": "Localhost", "address": "no_printing", "port": "1234"}
        )

        printer.create(
            {
                "name": "Password Printer",
                "system_name": "password_printer",
                "code": "1",
                "type": "pdf",
                "server_id": printer_server.id,
            }
        )

        printer.create(
            {
                "name": "Toshiba printer",
                "system_name": "toshiba_printer",
                "code": "20",
                "type": "toshiba",
                "server_id": printer_server.id,
            }
        )

        printer.create(
            {
                "name": "Zebra printer",
                "system_name": "zebra_printer",
                "code": "20",
                "type": "zebra",
                "server_id": printer_server.id,
            }
        )

        pack_op = self.picking.pack_operation_product_ids
        pack_op.ensure_one()

        # Print products labels and package labels
        domain = Print(self._default_header(), mock.MagicMock(name="Savepoint()"))
        request_params = Parameters(domain, action="requ")
        request_params.update(
            {
                "groupNum": self.picking.id,
                "printType": constants.PRINT_LABELS,  # Type of printing
                "printerNum": "20",  # Printer number
                "Usf01": 1,  # Number of copy
            }
        )

        # We cannot print a document !!!!
        result_str = domain.requ(request_params)
        result = self.format_result(result_str)

        self.assertEqual(result.respCode, str(constants.RESPONSE_CODE_ERROR))
        self.assertEqual(result.labelCD, "00")
        self.assertEqual(result.respMsg, "Error during printing")

        error_log = logger.search([("picking_id", "=", self.picking.id)])
        self.assertEqual(len(error_log), 1)
