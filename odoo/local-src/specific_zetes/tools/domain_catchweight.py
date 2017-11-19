# -*- coding: utf-8 -*-
import logging

from domain_interface import DomainInterface, Parameters
from .. import constants

_logger = logging.getLogger(__name__)


class Catchweight(DomainInterface):
    EXAMPLE_REQU = '208030828,2.2.3,3iV_101,REQU_CATCHWEIGHT,30,1,20170207,' \
                   '072929,30427733121295,000000001625844,,,,1,' \
                   '00000000162584400001,G,B,A,4,15,2520872,00709,01,,,,,,,' \
                   ',,000002,,67709,,,,,,,,,,,'
    EXAMPLE_RESP = '208030828,2.2.3,3iV_101,RESP_CATCHWEIGHT,30,1,20170207,' \
                   '072914,304277331212950,,,000000001625844,,,,1,' \
                   '00000000162584400001,2520872,000002,,67709,,,,,,,,,,'
    EXAMPLE_RESU = '208030828,2.2.3,3iV_101,RESU_CATCHWEIGHT,30,1,20170207,' \
                   '072930,30427733121306,000000001625844,,,,1,' \
                   '00000000162584400001,,,,,,,,,,67709,000002,,,,,,,,,'
    REQU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'itemPickSeqNum', 'pickLineId', 'sourceLC1', 'sourceLC2',
            'sourceLC3', 'sourceLC4', 'sourceLC5', 'productCode', 'Cri01',
            'Cri02', 'Cri03', 'Cri04', 'Cri05', 'Cri06', 'Cri07', 'Cri08',
            'Cri09', 'Cri10', 'effQty', 'totalCatchWeight', 'lotNumber',
            'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07',
            'Usf08', 'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'itemPickSeqNum', 'pickLineId', 'productCode',
            'effQty', 'totalCatchWeight', 'lotNumber', 'Usf01', 'Usf02',
            'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09',
            'Usf10')
    RESU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'itemSeqNum', 'lineId', 'assignmentType', 'unitOfMeasure',
            'seqWeightInput', 'weight', 'barcode', 'expiryDate',
            'destCarSeqNum', 'destCarId', 'lineIndicator', 'Usf01', 'Usf02',
            'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09',
            'Usf10')

    def requ(self, params):
        """
        Currently this method do nothing.
        We don't know why we have to use this method
        :param params:
        :return:
        """
        result = Parameters(self, action='resp')

        result.update({
            'respCode': constants.RESPONSE_CODE_OK,
            'groupNum': params.groupNum,
            'itemPickSeqNum': 1,
            'pickLineId': params.pickLineId,
            'productCode': params.productCode,
            'lotNumber': params.lotNumber,
            'effQty': params.effQty,
        })
        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Set the quantity (Usf02) on the stock move (lineId)
        Usf01 is the lot number
        :param params:
        :return:
        """
        move_id = params.lineId
        if not move_id:
            return

        move = self.request.env['stock.pack.operation'].sudo(self._user) \
            .browse(int(move_id))
        if not len(move):
            return

        # Retrieve the quantity
        quantity = params.Usf02 and float(params.Usf02) or 0

        # and the lot number
        lot_number = params.Usf01

        try:
            self.add_quantity(move_id, quantity, lot_number)
        except Exception as e:
            _logger.error(str(e))
            params.log(picking_id=move.picking_id.id,
                       operation_id=move_id,
                       exception=e)

    def add_quantity(self, move, quantity, lot_number=None):
        # If there is no lot number, it means that we don't care about lot
        # (tracking => without lot). We can simply add the new quantity.
        if not lot_number:
            move.qty_done += quantity
        else:
            # Otherwise we need to search for the lot in Odoo
            lot = self.request.env['stock.production.lot']\
                .sudo(self._user).search(
                [('product_id', '=', move.product_id.id),
                 ('checksum', '=', lot_number)])
            if lot:
                # When we have the lot, we will check if there no existing
                # quantity for this lot.
                pack_lot = \
                    move.pack_lot_ids\
                        .filtered(lambda line: line.lot_id.id == lot.id)

                # If there no existing line (quantity) for this lot
                # we will create a new line
                if not len(pack_lot):
                    move.pack_lot_ids.create({
                        'operation_id': move.id,
                        'qty': quantity,
                        'lot_id': lot.id,
                    })
                # Otherwise we set the quantity for this lot
                # We don't need to add the new quantity to the lot
                # because Zetes send one request by lot
                else:
                    pack_lot.write({'qty': quantity})

                # Set the final quantity on the move
                qty_done = move.qty_done + quantity
                move.write({
                    'qty_done': qty_done,
                })

