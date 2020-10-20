# -*- coding: utf-8 -*-
import logging

from domain_interface import DomainInterface, Parameters, Savepoint
from odoo import _

from .. import constants

_logger = logging.getLogger(__name__)


class Print(DomainInterface):
    EXAMPLE_REQU = (
        "208030828,2.2.3,3iV_101,REQU_PRINT,30,1,20170207,"
        "073426,304277331552660,000000001625844,,,,,"
        "03,X,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208030828,2.2.3,3iV_101,RESP_PRINT,30,1,20170207,"
        "073411,304277331552660,0,,000000001625844,,,,,,,,,,"
        "17,,,,,,,,,,"
    )
    EXAMPLE_RESU = ""
    REQU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "assignmentType",
        "printType",
        "printerNum",
        "destLocationId",
        "destCarSeqNum",
        "destCarId",
        "Usf01",
        "Usf02",
        "Usf03",
        "Usf04",
        "Usf05",
        "Usf06",
        "Usf07",
        "Usf08",
        "Usf09",
        "Usf10",
    )
    RESP = (
        "respCode",
        "respMsg",
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "printerNum",
        "destLocationId",
        "destLocationCD",
        "destCarSeqNum",
        "destCarId",
        "numOfLabels",
        "labelCD",
        "Usf01",
        "Usf02",
        "Usf03",
        "Usf04",
        "Usf05",
        "Usf06",
        "Usf07",
        "Usf08",
        "Usf09",
        "Usf10",
    )
    RESU = ()

    def requ(self, params):
        """
        Send a request to print a picking (groupNum) on a printer according
        his number (printNum) and his type (printType).
        There is two type of printing.
        The standard printing (PRINT_LABELS) will print product labels
        and package labels.
        The second type (PRINT_PASSPORT) will print a A4 sheet with products.
        This sheet will be used by a second picker to check the package.
        :param params:
        :return:
        """
        result = Parameters(self, action="resp")

        picking_id = params.groupNum
        if not picking_id:
            result = Parameters(self, action="resp")
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("No picking found with the ID %s") % picking_id,
                }
            )
            return result.format()
        picking_id = int(picking_id)

        picking = self.request.env["stock.picking"].browse(picking_id)
        picking._lock_rows()
        # Assign a checksum on the picking (print on the package label)
        picking.assign_picking_checksum()

        quantity = int(params.Usf01 or 0)

        print_type = params.printType
        printer_num = params.printerNum

        # Print the passport (see above)
        if print_type == constants.PRINT_PASSPORT:
            pick_aliment = self.request.env.ref("__setup__.stock_picking_type_ali")
            pick_frigo = self.request.env.ref("__setup__.stock_picking_type_froid")
            if picking.picking_type_id == pick_aliment:
                printer_code = constants.PRINTER_ALIMENT
            elif picking.picking_type_id == pick_frigo:
                printer_code = constants.PRINTER_FRIGO
            else:
                printer_code = constants.PRINTER_MEDICAMENT

            # The passport is always printed on the printer 1
            printer = (
                self.request.env["printing.printer"]
                .sudo()
                .search([("code", "=", printer_code), ("type", "=", "pdf")])
            )
            if not printer:
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Cannot found a printer"),
                        "labelCD": "00",
                    }
                )
                return result.format()

            try:
                picking.sudo().print_passport_report(printer_id=printer.id)
            except Exception as e:
                self.rollback_to_savepoint()
                _logger.error(str(e))
                params.log(picking_id=picking_id, exception=e)
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Error during printing"),
                        "labelCD": "00",  # Default code
                    }
                )
                return result.format()

        elif print_type == constants.PRINT_LABELS:

            with Savepoint(self.request.env.cr) as pack_savepoint:
                try:
                    # Create a pack for this picking
                    box = picking.put_in_pack()
                    if isinstance(box, dict):
                        box = self.request.env["stock.quant.package"].browse(
                            box["res_id"]
                        )
                    if box:
                        # Set the number of packages for this picking
                        box.nbr_packages = quantity
                except Exception:
                    pack_savepoint.rollback()

            printer_toshiba = (
                self.request.env["printing.printer"]
                .sudo()
                .search([("code", "=", printer_num), ("type", "=", "toshiba")])
            )
            printer_zebra = (
                self.request.env["printing.printer"]
                .sudo()
                .search([("code", "=", printer_num), ("type", "=", "zebra")])
            )

            if not printer_toshiba or not printer_zebra:
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Cannot found a printer"),
                        "labelCD": "00",  # Default code
                    }
                )
                return result.format()

            try:
                picking.sudo().print_products_label(printer_id=printer_toshiba.id)
                picking.sudo().print_packages_label(printer_id=printer_zebra.id)
            except Exception as e:
                self.rollback_to_savepoint()
                _logger.error(str(e))
                params.log(picking_id=picking_id, exception=e)
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Error during printing"),
                        "labelCD": "00",  # Default code
                    }
                )
                return result.format()

        result.update(
            {
                "respCode": constants.RESPONSE_CODE_OK,
                "groupNum": picking.id,
                "labelCD": picking.checksum or "00",
            }
        )

        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        There is no resu request for print
        :param params:
        :return:
        """
        return
