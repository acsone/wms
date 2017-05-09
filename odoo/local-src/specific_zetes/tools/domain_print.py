# -*- coding: utf-8 -*-
import logging

from odoo import _
from odoo.http import request

from domain_interface import DomainInterface, Parameters

_logger = logging.getLogger(__name__)

PRINT_PASSPORT = '03'
PRINT_LABELS = '04'


class Print(DomainInterface):
    EXAMPLE_REQU = '208030828,2.2.3,3iV_101,REQU_PRINT,30,1,20170207,' \
                   '073426,304277331552660,000000001625844,,,,,' \
                   '03,X,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030828,2.2.3,3iV_101,RESP_PRINT,30,1,20170207,' \
                   '073411,304277331552660,0,,000000001625844,,,,,,,,,,' \
                   '17,,,,,,,,,,'
    EXAMPLE_RESU = ''
    REQU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'assignmentType', 'printType', 'printerNum', 'destLocationId',
            'destCarSeqNum', 'destCarId', 'Usf01', 'Usf02', 'Usf03', 'Usf04',
            'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'printerNum', 'destLocationId', 'destLocationCD',
            'destCarSeqNum', 'destCarId', 'numOfLabels', 'labelCD', 'Usf01',
            'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
            'Usf09', 'Usf10')
    RESU = ()

    def requ(self, params):
        result = Parameters(self, action='resp')

        picking_id = params.groupNum
        if not picking_id:
            result = Parameters(self, action='resp')
            result.update({
                'respCode': 10,
                'respMsg': _('No picking found with the ID {}'
                             .format(picking_id))
            })
            return result.format()
        picking_id = int(picking_id)

        picking = request.env['stock.picking']\
            .sudo(self._user).browse(picking_id)

        # Assign a checksum on the picking (print on the package label)
        picking.assign_picking_checksum()

        try:
            # Create a pack for this picking
            picking.put_in_pack()
        except Exception:
            pass

        print_type = params.printType
        printer_num = params.printerNum

        if print_type == PRINT_PASSPORT:
            # The passport is always printed on the printer 1
            printer = request.env['printing.printer'].sudo() \
                .search([('code', '=', '1'), ('type', '=', 'pdf')])
            if not printer:
                result.update({
                    'respCode': 10,
                    'respMsg': _('Cannot found a printer'),
                    'labelCD': '00',
                })
                return result.format()

            try:
                picking.sudo().print_passport_report(printer=printer)
            except Exception as e:
                _logger.error(str(e))
                params.log(picking_id=picking_id, exception=e)
                result.update({
                    'respCode': 10,
                    'respMsg': _('Error during printing'),
                    'labelCD': '00',  # Default code
                })
                return result.format()

        elif print_type == PRINT_LABELS:
            printer_toshiba = request.env['printing.printer']\
                .sudo().search([('code', '=', printer_num),
                                ('type', '=', 'toshiba')])
            printer_zebra = request.env['printing.printer']\
                .sudo().search([('code', '=', printer_num),
                                ('type', '=', 'zebra')])

            if not printer_toshiba or not printer_zebra:
                result.update({
                    'respCode': 10,
                    'respMsg': _('Cannot found a printer'),
                    'labelCD': '00',  # Default code
                })
                return result.format()

            quantity = int(params.Usf01)
            try:
                picking.sudo().print_products_label(printer=printer_toshiba)
                picking.sudo().print_packages_label(quantity=quantity,
                                                    printer=printer_zebra)
            except Exception as e:
                _logger.error(str(e))
                params.log(picking_id=picking_id, exception=e)
                result.update({
                    'respCode': 10,
                    'respMsg': _('Error during printing'),
                    'labelCD': '00',  # Default code
                })
                return result.format()

        result.update({
            'respCode': 0,
            'groupNum': picking.id,
            'labelCD': picking.checksum or '00',
        })

        return result.format()

    def resu(self, params):
        return
