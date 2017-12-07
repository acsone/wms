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

        if isinstance(move_id, int):
            move_id = str(move_id)

        pack_operation_id = int(move_id.split('_')[0])

        move = self.request.env['stock.pack.operation'].sudo(self._user)\
            .browse(pack_operation_id)
        if not len(move):
            return

        try:
            # Retrieve the quantity
            real_qty = params.Usf02 and float(params.Usf02) or 0
            virtual_qty = self.check_picked_quantity(params, move, real_qty)
            # and the lot number
            lot_number = params.Usf01

            lot_id = None
            if lot_number:
                lot = self.request.env['stock.production.lot'] \
                    .sudo(self._user).search(
                    [('product_id', '=', move.product_id.id),
                     ('checksum', '=', lot_number)], limit=1)
                if lot:
                    lot_id = lot.id

            # If we receive a value for Usf03, it means that we have to
            # check if the available quantity (in Odoo) is the same than
            # the real quantity (say by the picker).
            actual_stock = params.Usf03
            if actual_stock or actual_stock == 0:
                self.check_actual_stock(params, move, actual_stock, lot_id)
                return

            picking = move.picking_id
            if move.zetes_state == constants.MOVE_FULL:
                reserve_rel_obj = \
                    self.request.env['pack.operation.reserve.rel']
                reserve_rel = reserve_rel_obj.sudo(self._user).search([
                    ('pack_operation_id', '=', move.id),
                    ('lot_id', '=', lot_id)
                ], limit=1, order="id DESC")

                if not reserve_rel:
                    error_message = "Reserve not found for move %s (lot %s)" \
                                    % (move.id, lot_id)
                    _logger.error(error_message)
                    params.log(picking_id=move.picking_id.id,
                               operation_id=pack_operation_id,
                               exception=error_message)
                    return

                reserve = reserve_rel.reserve_location_id
                move = move.split_pack_op(virtual_qty, reserve.id, lot_id)
            elif picking.zetes_picking_type == constants.RESERVE_ASSIGNMENT \
                    and move.product_qty > virtual_qty:
                location_dest_id = move.location_id.id
                new_qty = move.product_qty - virtual_qty
                new_move = \
                    move.split_pack_op(new_qty, location_dest_id, lot_id)
                new_move.add_qty(new_qty, lot_id)

            move.add_qty(virtual_qty, lot_id)

        except Exception as e:
            _logger.error(str(e))
            params.log(picking_id=move.picking_id.id,
                       operation_id=pack_operation_id,
                       exception=e)

    def check_actual_stock(self, params, move, actual_stock, lot_id=None):
        """
        Check if the actual quantity in stock equals the available quantity
        in Odoo.
        :param params:
        :param move:
        :param actual_stock:
        :param lot_id:
        :return:
        """
        available_qty_query = """
        SELECT sum(quant.qty)
        FROM stock_quant AS quant
        WHERE quant.product_id = %s
        AND quant.location_id = %s
        AND quant.reservation_id IS NULL
        """
        query_values = [move.product_id.id, move.location_id.id]

        # We cannot handle ZeroCheck with lot
        # if lot_id:
        #     available_qty_query += " AND quant.lot_id = %s"
        #     query_values.append(lot_id)
        # else:
        #     available_qty_query += " AND quant.lot_id IS NULL"

        self.request.env.cr.execute(available_qty_query, tuple(query_values))
        query_result = self.request.env.cr.fetchone()
        available_qty = query_result and query_result[0] or 0

        if available_qty != actual_stock:
            error_message = "The theoretical stock (%s) is different" \
                            " from the actual stock (%s) for" \
                            " the product %s in the location %s" % \
                            (available_qty,
                             actual_stock,
                             move.product_id.display_name,
                             move.location_id.display_name)
            if lot_id:
                lot = self.request.env['stock.production.lot']\
                    .sudo(self._user).browse(lot_id)
                error_message += " (lot %s)" % lot.name

            _logger.error(error_message)
            params.log(picking_id=move.picking_id.id,
                       operation_id=move.id,
                       exception=error_message)

    def check_picked_quantity(self, params, move, picked_quantity):
        """
        Zetes allows (only for Parking and Reserve) to take a quantity
        greater than the requested quantity. However Odoo refuse this case.
        If the picked quantity is greater than the requested quantity we need
        to virtually change the picked quantity with the requested quantity
        and send an email to warm the manager.
        :param move:
        :param picked_quantity:
        :return:
        """
        total_picked_quantity = move.qty_done + picked_quantity
        max_allowed_quantity = move.product_qty

        if total_picked_quantity > max_allowed_quantity:
            error_message = "The total picked quantity (%s) is greater than" \
                            " the requested quantity (%s) for the product " \
                            "%s (Operation ID %s)" % \
                            (total_picked_quantity,
                             max_allowed_quantity,
                             move.product_id.display_name,
                             move.id)
            _logger.error(error_message)
            params.log(picking_id=move.picking_id.id,
                       operation_id=move.id,
                       exception=error_message)
            return move.product_qty - move.qty_done

        return picked_quantity
