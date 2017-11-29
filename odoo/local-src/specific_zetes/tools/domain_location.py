# -*- coding: utf-8 -*-
from odoo import _

from domain_interface import DomainInterface, Parameters
from .. import constants


class Location(DomainInterface):
    EXAMPLE_REQU = '208092661,2.2.3,3iV_101,REQU_LOCATION,58,1,20170207,' \
                   '073526,584277331622644,000000001625845,,,,' \
                   '00000000162584500009,,,A,A,1,0,B2,3265295,' \
                   '00217,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208092661,2.2.3,3iV_101,RESP_LOCATION,58,1,' \
                   '20170207,073438,584277331622644,0,,000000001625845,,' \
                   '000000001625845,,00000000162584500009,,00,A,A,1,0,B2,' \
                   '95,,000538,,01,3265295,VIRBAC HPM CAT ADULT NEUTERED 3KG' \
                   ',,,,,,00219,00157,00000,00000,00000,00000,000522,,,,'
    EXAMPLE_RESU = ''
    REQU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'lineId',
            'itemSeqNum', 'assignmentType', 'Cri01', 'Cri02', 'Cri03', 'Cri04',
            'Cri05', 'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10', 'Usf01',
            'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
            'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'lineId', 'itemSeqNum', 'locationStatus', 'lC1',
            'lC2', 'lC3', 'lC4', 'lC5', 'lCCD', 'lCBarcode', 'quantity',
            'promptInfo', 'unitOfMeasure', 'productCode', 'productDescription',
            'productGroupCode', 'productProperty1', 'productProperty2',
            'productProperty3', 'productBarcode', 'Usf01', 'Usf02', 'Usf03',
            'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESU = ()

    def requ(self, params):
        """
        Return a list of existing lots for a stock pack operation (lineId).
        This method is used by Zetes when the picker doesn't find the right
        lot or we need quantity available.
        :param params:
        :return:
        """
        result = Parameters(self, action='resp')

        move_id = params.lineId
        if not move_id:
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('No picking found')
            })
            return result.format()

        if isinstance(move_id, int):
            move_id = str(move_id)

        move_id_list = move_id.split('_')
        if len(move_id_list) == 2:
            pack_operation_id = int(move_id_list[0])
            lot_id = int(move_id_list[1])
        else:
            pack_operation_id = int(move_id)
            lot_id = None

        move = self.request.env['stock.pack.operation'].sudo(self._user)\
            .browse(pack_operation_id)
        if not len(move):
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('No picking found')
            })
            return result.format()

        product = move.product_id

        result.update({
            'respCode': constants.RESPONSE_CODE_OK,
            'headerNum': None,
            'productCode': product.default_code,
            'productDescription': product.name,
            'quantity': product.qty_available,  # Total quantity
            'Usf07': product.virtual_available,  # Stock available
        })

        location = self.request.env['stock.location'].sudo(self._user) \
            .search([('zone', '=', params.Cri01),
                     ('corridor', '=', params.Cri02),
                     ('shelf', '=', params.Cri03),
                     ('height', '=', params.Cri04),
                     ('box', '=', params.Cri05)],
                    limit=1)

        if not location:
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('Location %s%s%s%s%s not found' % (params.Cri01,
                                                                params.Cri02,
                                                                params.Cri03,
                                                                params.Cri04,
                                                                params.Cri05))
            })
            return result.format()

        if move.picking_id.zetes_picking_type == constants.PARKING_ASSIGNMENT:
            self.request.env['pack.operation.reserve.rel'].sudo(self._user)\
                .create({
                    'pack_operation_id': move.id,
                    'reserve_location_id': location.id,
                    'lot_id': lot_id
                })

        result.update({
            'lC1': location.zone,
            'lC2': location.corridor,
            'lC3': location.shelf,
            'lC4': location.height,
            'lC5': location.box,
            'lCCD': location.get_checksum(),
        })

        lots = self.request.env['stock.production.lot'].sudo(self._user) \
            .search([('product_id', '=', product.id),
                     ('is_archived', '=', False)
                     ],
                    order='life_date',
                    limit=5)

        # Lots are stored in the value Usf0#LOT_NUMBER (eg: Usf01)
        index = 0
        for lot in lots:
            index += 1
            setattr(result, 'Usf0{}'.format(index), lot.checksum)

        # Search a specific lot
        specific_lot = self.request.env['stock.production.lot']\
            .sudo(self._user).search([('checksum', '=', params.Cri07),
                                      ('product_id', '=', product.id),
                                      ('is_archived', '=', False)],
                                     limit=1)
        if specific_lot:
            result.Usf06 = specific_lot.checksum

        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        There is no resu request for location
        :param params:
        :return:
        """
        return
