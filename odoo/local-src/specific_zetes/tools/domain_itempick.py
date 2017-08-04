# -*- coding: utf-8 -*-
import logging

from odoo import _

from domain_interface import DomainInterface, Parameters
from .. import constants

_logger = logging.getLogger(__name__)


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
    REQU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'tripCounter', 'Cri01', 'Cri02', 'Cri03', 'Cri04', 'Cri05',
            'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10', 'Usf01', 'Usf02',
            'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09',
            'Usf10')
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
    RESU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'itemPickSeqNum', 'pickLineId', 'lineIndicator', 'reqQty',
            'effQtySourceLC', 'effQtyAltSourceLC', 'pickStatus', 'tripCounter',
            'unitOfMeasure', 'totalCatchWeight', 'lotNumber', 'productBarcode',
            'sourceLCBarcode', 'altSourceLCBarcode', 'effQtyDestCar01',
            'effQtyDestCar02', 'effQtyDestCar03', 'effQtyDestCar04',
            'effQtyDestCar05', 'effQtyDestCar06', 'effQtyDestCar07',
            'effQtyDestCar08', 'effQtyDestCar09', 'effQtyDestCar10',
            'effDestCarId01', 'effDestCarId02', 'effDestCarId03',
            'effDestCarId04', 'effDestCarId05', 'effDestCarId06',
            'effDestCarId07', 'effDestCarId08', 'effDestCarId09',
            'effDestCarId10', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05',
            'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')

    def requ(self, params):
        """
        Return a list of stock pack operation according the picking ID
        Param: groupNum (picking_id)
        :param params:
        :return:
        """
        # If there is not Picking ID we cannot assign a stock move
        if not params.groupNum:
            result = Parameters(self, action='resp')
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': 'No picking found'
            })
            return result.format()

        picking_id = params.groupNum
        if not picking_id:
            result = Parameters(self, action='resp')
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('No picking found with the ID {}'
                             .format(picking_id))
            })
            return result.format()
        picking_id = int(picking_id)

        # Cri01 define the order (01 => from the end to the start)
        if params.Cri01 == '1':
            order_by = 'location_name DESC'
        else:
            order_by = 'location_name ASC'

        print_price_query = """
        SELECT partner.is_price_on_labels
        FROM stock_picking AS picking
          INNER JOIN res_partner AS partner ON picking.partner_id = partner.id
        WHERE picking.id = %s;
        """
        self.request.env.cr.execute(print_price_query, (picking_id, ))
        print_price_result = self.request.env.cr.fetchone()
        if print_price_result and print_price_result[0]:
            is_print_price = True
        else:
            is_print_price = False

        # If the picking type is 'Aliment' whe need to print on portable pinter
        query = "SELECT picking_type_id FROM stock_picking WHERE id = %s"
        self.request.env.cr.execute(query, (picking_id, ))
        query_result = self.request.env.cr.fetchone()

        type_food = self.request.env['stock.picking.type'].search([
            ('food_type', '=', True)])
        if query_result and type_food and query_result[0] == type_food.id:
            print_on_portable_printer = '1'
        else:
            print_on_portable_printer = '0'

        sequence = 1
        result = []
        # Search all pack operations for this picking
        lines = self.request.env['stock.pack.operation'].sudo(self._user)\
            .search([('picking_id', '=', picking_id)],
                    order=order_by)
        # Filter lines
        # We want only operation with a quantity to to done different
        # than the quantity done.
        # The state of the line must be
        # "OP_DEFAULT", "OP_SKIPPED" or "OP_CANCELED"
        lines = lines\
            .filtered(lambda line: int(line.qty_done) != int(line.product_qty)
                      and line.zetes_state in [constants.OP_DEFAULT,
                                               constants.OP_SKIPPED,
                                               constants.OP_CANCELED])

        if not lines:
            error_message = _('There is no lines for the picking {}'
                              .format(picking_id))

            self.request.env['stock.picking'].sudo(self._user)\
                .browse(picking_id).write(
                {'is_zetes_error': True,
                 'traceback': error_message})

            result = Parameters(self, action='resp')
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': error_message
            })
            return result.format()

        for line in lines:
            line_values = Parameters(self)
            line_values.update({
                'respCode': constants.RESPONSE_CODE_OK,
                'groupNum': picking_id,
                'pickLineId': line.id,
                'reqDestCarSeqNum': 1,
                'reqQty': format(int(line.product_qty), '0%d' % 6),
                'effQty': format(int(line.qty_done), '0%d' % 6),
                'pickStatus': constants.OP_DEFAULT,
                'tripCounter': 1,
            })

            product = line.product_id

            line_values.update({
                'productCode': product.default_code,
                'productDescription': product.name,
                'productProperty1': None,
                'productProperty2': print_on_portable_printer,
                'lessQtyAllowed': 1,  # Constant value
                'moreQtyAllowed': 0,  # Constant value
                'catchWeightFlag': 0,  # Constant value
                'cycleCountFlag': 0,  # Constant value
                'expiryDateCheckFlag': 0,  # Constant value
                'productBarcode': product.barcode,
                'scanProductBarcode': 0,  # Constant value
                'UOMPrompt': line.product_uom_id.name,
                'itemPickSeqNum': sequence,
            })

            if is_print_price:
                line_values.Usf07 = line.product_id.list_price

            if product.tracking == 'lot':
                line_values.lotTrackingFlag = 1
            else:
                line_values.lotTrackingFlag = 0

            # # To define the unit of measure only for unit
            # # different than "Unit", uncomment following lines
            # # and remove "UOMPrompt" in the line_values (above)
            # default_uom = request.env.ref('product.product_uom_unit')
            # if line.product_uom_id != default_uom:
            #     line_values.UOMPrompt = line.product_uom_id.name

            location = line.location_id
            if not location:
                line_values.update({
                    'respCode': constants.RESPONSE_CODE_ERROR,
                    'respMsg': _('Location not found for the product {}'
                                 .format(product.name)),
                })
                result.append(line_values)
                continue

            # Set coordonates location of the bin
            line_values.update({
                'sourceLC1': location.zone,
                'sourceLC2': location.corridor,
                'sourceLC3': location.shelf,
                'sourceLC4': location.height,
                'sourceLC5': location.box,
                'sourceLCCD': location.get_checksum(),
            })

            # Send 5 first lots for this products (ordered by life date)
            lots = self.request.env['stock.production.lot'].sudo(self._user)\
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
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Change the state of the current stock pack operation (pickLineId)
        If the state is OP_CANCELED we remove all lots for this operation
        :param params:
        :return:
        """
        if not params.pickLineId:
            return
        move_id = int(params.pickLineId)

        move = self.request.env['stock.pack.operation']\
            .sudo(self._user).browse(move_id)
        if not len(move):
            return

        try:
            status = params.pickStatus
            if status:
                move.sudo(self._user).write({
                    'zetes_state': status
                })

                # If status == OP_CANCELED => remove all actions for this line
                if status == constants.OP_CANCELED:
                    move.pack_lot_ids.unlink()
                    move.save()

        except Exception as e:
            _logger.error(str(e))
            params.log(picking_id=move.picking_id.id,
                       operation_id=move_id,
                       exception=e)
