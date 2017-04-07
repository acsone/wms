# -*- coding: utf-8 -*-
from odoo import _
from odoo.http import request

from domain_interface import DomainInterface, Parameters


class Itempick(DomainInterface):
    EXAMPLE_REQU = '208030828,2.2.3,3iV_101,REQU_ITEMPICK,30,1,20170207,' \
                   '072904,30427733118044,000000001625844,,,,1,' \
                   '0,,,,,,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030828,2.2.3,3iV_101,RESP_ITEMPICK,30,1,20170207,' \
                   '072849,30427733118044,0,,000000001625844,,,,00001,' \
                   '00000000162584400001,1,1,,G,B,A,4,15,16,,,,,,,,,,' \
                   '000002,000000,00,Aucune indication,01,2520872,' \
                   'LAXANORM 100GR,,00006,0,,1,0,0,0,1,0,,pièce,,,,,,,,' \
                   '0,67709,00000,00000,00000,00000,,0016.65,,,'
    EXAMPLE_RESU = '208030828,2.2.3,3iV_101,RESU_ITEMPICK,30,1,20170207,' \
                   '072931,30427733121317,000000001625844,,,,1,' \
                   '00000000162584400001,,000002,000002,,' \
                   '01,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,'
    REQU = (
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'tripCounter',
    'Cri01', 'Cri02', 'Cri03', 'Cri04', 'Cri05', 'Cri06', 'Cri07', 'Cri08',
    'Cri09', 'Cri10', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06',
    'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'itemPickSeqNum', 'pickLineId', 'tripCounter',
            'reqDestCarSeqNum', 'reqDestCarSeqCD', 'sourceLC1', 'sourceLC2',
            'sourceLC3', 'sourceLC4', 'sourceLC5', 'sourceLCCD',
            'sourceLCBarcode', 'altSourceLC1', 'altSourceLC2', 'altSourceLC3',
            'altSourceLC4', 'altSourceLC5', 'altSourceLCCD',
            'altSourceLCBarcode', 'lineIndicator', 'reqQty', 'effQty',
            'pickStatus', 'promptInfo', 'unitOfMeasure', 'productCode',
            'productDescription', 'productGroupCode', 'productProperty1',
            'productProperty2', 'productProperty3', 'lessQtyAllowed',
            'moreQtyAllowed', 'catchWeightFlag', 'cycleCountFlag',
            'lotTrackingFlag', 'expiryDateCheckFlag', 'lotNumber', 'UOMPrompt',
            'singlesInUOM', 'minBlockCW', 'maxBlockCW', 'minAllowedCW',
            'maxAllowedCW', 'expiryDate', 'productBarcode',
            'scanProductBarcode', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05',
            'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESU = (
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'itemPickSeqNum',
    'pickLineId', 'lineIndicator', 'reqQty', 'effQtySourceLC',
    'effQtyAltSourceLC', 'pickStatus', 'tripCounter', 'unitOfMeasure',
    'totalCatchWeight', 'lotNumber', 'productBarcode', 'sourceLCBarcode',
    'altSourceLCBarcode', 'effQtyDestCar01', 'effQtyDestCar02',
    'effQtyDestCar03', 'effQtyDestCar04', 'effQtyDestCar05', 'effQtyDestCar06',
    'effQtyDestCar07', 'effQtyDestCar08', 'effQtyDestCar09', 'effQtyDestCar10',
    'effDestCarId01', 'effDestCarId02', 'effDestCarId03', 'effDestCarId04',
    'effDestCarId05', 'effDestCarId06', 'effDestCarId07', 'effDestCarId08',
    'effDestCarId09', 'effDestCarId10', 'Usf01', 'Usf02', 'Usf03', 'Usf04',
    'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')

    def requ(self, params):
        if not params.groupNum:
            result = Parameters(self, action='resp')
            result.update({
                'respCode': 10,
                'respMsg': 'No picking found'
            })
            return result.format()

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

        if params.Cri01 == '1':
            order_by = 'location_name DESC'
        else:
            order_by = 'location_name ASC'

        sequence = 1
        result = []
        lines = request.env['stock.pack.operation'].sudo(self._user)\
            .search([('picking_id', '=', picking_id)],
                    order=order_by)
        for line in lines:
            if line.zetes_state and line.zetes_state not in ['00', '03']:
                continue

            line_values = Parameters(self)
            line_values.update({
                'groupNum': picking_id,
                'pickLineId': line.id,
                'reqDestCarSeqNum': 1,
                'reqQty': format(int(line.product_qty), '0%d' % 6),
                'effQty': format(int(line.qty_done), '0%d' % 6),
                'pickStatus': '00',
                'tripCounter': 1,
            })

            product = line.product_id

            line_values.update({
                'productCode': product.default_code,
                'productDescription': product.name,
                'productProperty1': None,
                'productProperty2': '0', # TODO
                'lessQtyAllowed': 1,
                'moreQtyAllowed': 0,
                'catchWeightFlag': 0,
                'cycleCountFlag': 0,
                'expiryDateCheckFlag': 0,
                'productBarcode': product.barcode,
                'scanProductBarcode': 0,
                'UOMPrompt': line.product_uom_id.name,
                'itemPickSeqNum': sequence,
            })

            if product.tracking == 'lot':
                line_values.lotTrackingFlag = 1
            else:
                line_values.lotTrackingFlag = 0

            # default_uom = request.env.ref('product.product_uom_unit')
            # if line.product_uom_id != default_uom:
            #     line_values.UOMPrompt = line.product_uom_id.name

            location = line.location_id
            if not location:
                line_values.update({
                    'respCode': 10,
                    'respMsg': _('Location not found for the product {}'
                                 .format(product.name)),
                })
                result.append(line_values)
                continue

            line_values.update({
                'sourceLC1': location.zone,
                'sourceLC2': location.corridor,
                'sourceLC3': location.shelf,
                'sourceLC4': location.height,
                'sourceLC5': location.box,
                'sourceLCCD': location.get_checksum(),
            })

            lots = request.env['stock.production.lot'].sudo(self._user)\
                .search([('product_id', '=', product.id),
                         ('is_archived', '=', False)
                         ],
                        order='life_date',
                        limit=5)
            index = 0
            for lot in lots:
                index += 1
                setattr(line_values, 'Usf0{}'.format(index), lot.checksum)

            result.append(line_values)
            sequence += 1

        return '\n'.join([line.format() for line in result])

    def resu(self, params):
        if not params.pickLineId:
            return
        move_id = int(params.pickLineId)

        move = \
            request.env['stock.pack.operation'].sudo(self._user).browse(move_id)
        if not len(move):
            return

        status = params.pickStatus
        if status:
            move.sudo(self._user).write({
                'zetes_state': status
            })
