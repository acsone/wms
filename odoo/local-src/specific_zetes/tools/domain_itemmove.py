# -*- coding: utf-8 -*-
import logging

from odoo import _

from domain_interface import DomainInterface, Parameters
from .. import constants

_logger = logging.getLogger(__name__)


class Itemmove(DomainInterface):
    REQU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'itemMoveType', 'Cri01', 'Cri02', 'Cri03', 'Cri04', 'Cri05',
            'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10', 'Usf01', 'Usf02',
            'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09',
            'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'itemMoveSeqNum', 'moveLineId', 'itemMoveType',
            'sourceLC1', 'sourceLC2', 'sourceLC3', 'sourceLC4', 'sourceLC5',
            'sourceLCCD', 'sourceLCBarcode', 'destLC1', 'destLC2', 'destLC3',
            'destLC4', 'destLC5', 'destLCCD', 'destLCBarcode', 'lineIndicator',
            'reqQty', 'effQty', 'moveStatus', 'promptInfo', 'unitOfMeasure',
            'productCode', 'productDescription', 'productGroupCode',
            'productProperty1', 'productProperty2', 'productProperty3',
            'productBarcode', 'scanProductBarcode', 'Usf01', 'Usf02', 'Usf03',
            'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESU = ('groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
            'itemMoveSeqNum', 'moveLineId', 'lineIndicator', 'itemMoveType',
            'quantity', 'moveStatus', 'unitOfMeasure', 'lotNumber',
            'sourceLC1', 'sourceLC2', 'sourceLC3', 'sourceLC4', 'sourceLC5',
            'sourceLCCD', 'sourceLCBarcode', 'destLCPresentFlag', 'destLC1',
            'destLC2', 'destLC3', 'destLC4', 'destLC5', 'destLCCD',
            'destLCBarcode', 'productBarcode', 'Usf01', 'Usf02', 'Usf03',
            'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')

    def requ(self, params):
        """
        Return a list or only one item (according the move type)
        of pack operation.

        There are two type of move type (itemMoveType):
        - Load (constants.MOVE_TYPE_LOAD):
            The picker will take products from parking to shelf.
            This method will return several lines for this request
        - Put (constants.MOVE_TYPE_PUT):
            The picker will take a product from the reserve the shelf.
            This method will return only one line at once
        :param params:
        :return:
        """
        move_type = params.itemMoveType

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

        if params.itemMoveType == constants.MOVE_TYPE_LOAD:
            lines = self.get_load_lines(params, picking_id)
        elif params.itemMoveType == constants.MOVE_TYPE_PUT:
            lines = self.get_put_lines(params, picking_id)
        else:
            _logger.error('itemMoveType %s unknown' % params.itemMoveType)
            lines = []

        if not lines:
            error_message = _('There is no lines for the picking {}'
                              .format(picking_id))

            self.request.env['stock.picking'].sudo(self._user) \
                .browse(picking_id).write(
                {'is_zetes_error': True,
                 'traceback': error_message})

            result = Parameters(self, action='resp')
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': error_message
            })
            return result.format()

        sequence = 1
        result = []
        for line, lot, qty, load_or_unload in lines:
            line_values = Parameters(self)

            location = line.location_id
            location_dest_id = line.location_dest_id
            product = line.product_id

            # For load and unload, Zetes will always send a RESU_CATCHWEIGHT
            # with the quantity. However we don't want to impute Odoo for
            # unload picking. The only way to ignore all RESU_CATCHWEIGHT
            # for unload picking is to send a false line ID (0)
            if load_or_unload == constants.MOVE_UNLOAD:
                line_id = 0
            else:
                line_id = line.id

            line_values.update({
                'respCode': constants.RESPONSE_CODE_OK,
                'groupNum': picking_id,
                'moveLineId': line_id,
                'itemMoveSeqNum': sequence,
                'itemMoveType': move_type,
                'reqQty': format(int(qty), '0%d' % 6),
                'effQty': format(int(line.qty_done), '0%d' % 6),
                'productCode': product.default_code,
                'productDescription': product.name,
                'productBarcode': product.barcode,
                'scanProductBarcode': 0,  # Constant value
                'sourceLC1': location.zone,
                'sourceLC2': location.corridor,
                'sourceLC3': location.shelf,
                'sourceLC4': location.height,
                'sourceLC5': location.box,
                'sourceLCCD': location.get_checksum(),
            })

            # TODO Please confirm this
            # If it is a reserved quantity the location destination
            # is the same than the current location
            if move_type == constants.MOVE_TYPE_PUT:
                location_dest_id = location

            line_values.update({
                'destLC1': location_dest_id.zone,
                'destLC2': location_dest_id.corridor,
                'destLC3': location_dest_id.shelf,
                'destLC4': location_dest_id.height,
                'destLC5': location_dest_id.box,
                'destLCCD': location_dest_id.get_checksum(),
            })

            if lot:
                line_values.Usf01 = lot.checksum
            else:
                line_values.Usf01 = product.default_code[:3]

            # Set the type of load (load or unload) move type "Load"
            if move_type == constants.MOVE_TYPE_LOAD:
                line.Usf02 = load_or_unload

            result.append(line_values)
            sequence += 1

        return '\n'.join([line.format() for line in result])

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Change the state of the current stock pack operation (moveLineId)
        :param params:
        :return:
        """
        move_type = params.itemMoveType

        if not params.moveLineId:
            return
        move_id = int(params.moveLineId)

        move = self.request.env['stock.pack.operation']\
            .sudo(self._user).browse(move_id)
        if not len(move):
            return

        try:
            status = params.moveStatus
            if status:
                move.sudo(self._user).write({
                    'zetes_state': status
                })

            if status == constants.MOVE_DEFAULT or \
                    (move_type == constants.MOVE_TYPE_PUT
                     and status == constants.MOVE_FULL):
                self.complete_operation(params)




        except Exception as e:
            _logger.error(str(e))
            params.log(picking_id=move.picking_id.id,
                       operation_id=move_id,
                       exception=e)

    def get_load_lines(self, params, picking_id):

        # Cri01 define the order (01 => from the end to the start)
        if params.Cri01 == '1':
            order_by = 'location_name DESC'
        else:
            order_by = 'location_name ASC'

        # Search all pack operations for this picking
        # The state of the line must be
        # "OP_DEFAULT", "OP_SKIPPED" or "OP_CANCELED"
        lines = self.request.env['stock.pack.operation'].sudo(self._user) \
            .search([('picking_id', '=', picking_id),
                     ('zetes_state', 'in', [constants.OP_DEFAULT,
                                            constants.OP_SKIPPED,
                                            constants.OP_CANCELED])],
                    order=order_by)
        # Filter lines
        # We want only operation with a quantity to to done different
        # than the quantity done.
        lines = lines \
            .filtered(lambda line: int(line.qty_done) < int(line.product_qty))

        reserved_quants_query = """
        SELECT sum(quant.qty)
        FROM stock_quant AS quant 
        WHERE quant.location_id = %
        AND quant.product_id = %s
        AND quant.reservation_id IS NOT NULL;
        """

        reserved_lines = []
        put_away_lines = []
        for line in lines:
            line_qty = put_away_qty = line.product_qty

            # Check if there are some reserved quantities
            self.request.env.cr.execute(
                reserved_quants_query, (line.location_id.id,
                                        line.product_id.id))
            query_result = self.request.env.cr.fetchone()
            if query_result:
                reserved_qty = query_result[0]
                put_away_qty = line_qty - reserved_qty

                reserved_lines.append(
                    (line, None, reserved_qty, constants.MOVE_UNLOAD))

            if not line.pack_lot_ids:
                put_away_lines.append(
                    (line, None, put_away_qty, constants.MOVE_LOAD))
            else:
                pack_lots = line.pack_lot_ids.filtered(
                    lambda lot: lot.qty < lot.qty_todo
                )
                for pack_lot in pack_lots:
                    put_away_lines.append(
                        (line, pack_lot.lot_id,
                         pack_lot.qty, constants.MOVE_LOAD)
                    )

        return reserved_lines + put_away_lines

    def get_put_lines(self, params, picking_id):
        # Search ONLY ONE pack operations for this picking
        # The state of this line must be
        # "MOVE_DEFAULT" or "MOVE_SKIPPED"
        lines = self.request.env['stock.pack.operation'].sudo(self._user) \
            .search([('picking_id', '=', picking_id),
                     ('zetes_state', 'in', [constants.MOVE_DEFAULT,
                                            constants.MOVE_SKIPPED])])

        # Filter line
        # We want only operation with a quantity to to done different
        # than the quantity done.
        lines = lines.filtered(
            lambda x: int(x.qty_done) != int(x.product_qty))

        if not lines:
            return []

        # Take the first line
        line = lines.pop(0)
        if not line.pack_lot_ids:
            return [line, None, line.product_qty, None]

        pack_lots = \
            line.pack_lot_ids.filtered(lambda lot: lot.qty < lot.qty_todo)
        if not pack_lots:
            _logger.error('Error with the line %s (picking %s):\n'
                          'No valid lots' % (line.id, picking_id))
            return []
        pack_lot = pack_lots[0]

        return [line, pack_lot.lot_id, pack_lot.qty, None]
