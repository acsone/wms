# -*- coding: utf-8 -*-
from odoo import _
from odoo.http import request

from domain_interface import DomainInterface, Parameters


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
    REQU = (
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'itemPickSeqNum',
    'pickLineId', 'sourceLC1', 'sourceLC2', 'sourceLC3', 'sourceLC4',
    'sourceLC5', 'productCode', 'Cri01', 'Cri02', 'Cri03', 'Cri04', 'Cri05',
    'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10', 'effQty', 'totalCatchWeight',
    'lotNumber', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07',
    'Usf08', 'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'itemPickSeqNum', 'pickLineId', 'productCode',
            'effQty', 'totalCatchWeight', 'lotNumber', 'Usf01', 'Usf02',
            'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09',
            'Usf10')
    RESU = (
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'itemSeqNum',
    'lineId', 'assignmentType', 'unitOfMeasure', 'seqWeightInput', 'weight',
    'barcode', 'expiryDate', 'destCarSeqNum', 'destCarId', 'lineIndicator',
    'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
    'Usf09', 'Usf10')

    def requ(self, params):
        """
        Currently this method do nothing.
        We don't know why we have to use this method
        :param params:
        :return:
        """
        result = Parameters(self, action='resp')

        result.update({
            'respCode': 0,
            'groupNum': params.groupNum,
            'itemPickSeqNum': 1,
            'pickLineId': params.pickLineId,
            'productCode': params.productCode,
            'lotNumber': params.lotNumber,
            'effQty': params.effQty,
        })
        return result.format()

    def resu(self, params):
        move_id = params.lineId

        if not move_id:
            return

        move = request.env['stock.pack.operation'].sudo(self._user)\
            .browse(int(move_id))
        if not len(move):
            return

        qty_done_by_lot = params.Usf02 and float(params.Usf02) or 0

        lot_number = params.Usf01
        if not lot_number:
            return

        lot = request.env['stock.production.lot'].sudo(self._user)\
            .search([('product_id', '=', move.product_id.id),
                     ('checksum', '=', lot_number)])
        if lot:
            pack_lot = \
                move.pack_lot_ids\
                    .filtered(lambda line: line.lot_id.id == lot.id)

            if not len(pack_lot):
                move.pack_lot_ids.create({
                    'operation_id': move.id,
                    'qty': qty_done_by_lot,
                    'lot_id': lot.id,
                })
            else:
                pack_lot.write({'qty': qty_done_by_lot})

            qty_done = move.qty_done + qty_done_by_lot
            move.write({
                'qty_done': qty_done,
            })
