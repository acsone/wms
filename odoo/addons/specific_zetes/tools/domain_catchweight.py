# -*- coding: utf-8 -*-
import logging

from domain_interface import DomainInterface, Parameters
from odoo import _, fields

from .. import constants

_logger = logging.getLogger(__name__)


class Catchweight(DomainInterface):
    EXAMPLE_REQU = (
        "208030828,2.2.3,3iV_101,REQU_CATCHWEIGHT,30,1,20170207,"
        "072929,30427733121295,000000001625844,,,,1,"
        "00000000162584400001,G,B,A,4,15,2520872,00709,01,,,,,,,"
        ",,000002,,67709,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208030828,2.2.3,3iV_101,RESP_CATCHWEIGHT,30,1,20170207,"
        "072914,304277331212950,,,000000001625844,,,,1,"
        "00000000162584400001,2520872,000002,,67709,,,,,,,,,,"
    )
    EXAMPLE_RESU = (
        "208030828,2.2.3,3iV_101,RESU_CATCHWEIGHT,30,1,20170207,"
        "072930,30427733121306,000000001625844,,,,1,"
        "00000000162584400001,,,,,,,,,,67709,000002,,,,,,,,,"
    )
    REQU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "itemPickSeqNum",
        "pickLineId",
        "sourceLC1",
        "sourceLC2",
        "sourceLC3",
        "sourceLC4",
        "sourceLC5",
        "productCode",
        "Cri01",
        "Cri02",
        "Cri03",
        "Cri04",
        "Cri05",
        "Cri06",
        "Cri07",
        "Cri08",
        "Cri09",
        "Cri10",
        "effQty",
        "totalCatchWeight",
        "lotNumber",
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
        "itemPickSeqNum",
        "pickLineId",
        "productCode",
        "effQty",
        "totalCatchWeight",
        "lotNumber",
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
    RESU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "itemSeqNum",
        "lineId",
        "assignmentType",
        "unitOfMeasure",
        "seqWeightInput",
        "weight",
        "barcode",
        "expiryDate",
        "destCarSeqNum",
        "destCarId",
        "lineIndicator",
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

    def requ(self, params):
        """
        Currently this method do nothing.
        We don't know why we have to use this method
        :param params:
        :return:
        """
        result = Parameters(self, action="resp")

        line_id = params.pickLineId
        if not line_id:
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("No picking found"),
                }
            )
            return result.format()

        get_lot_query = """
        SELECT lot.life_date
        FROM stock_production_lot AS lot
            INNER JOIN product_product pp on lot.product_id = pp.id
            INNER JOIN product_template pt on pp.product_tmpl_id = pt.id
        WHERE pt.default_code = %s
        AND lot.voice_identifier = %s
        LIMIT 1;
        """

        self.request.env.cr.execute(
            get_lot_query, (params.productCode, params.lotNumber)
        )
        query_result = self.request.env.cr.fetchone()
        if query_result:
            life_date_str = query_result[0]
            if life_date_str:
                life_date = fields.Date.from_string(life_date_str)
                result.Usf01 = life_date.strftime("%d%m%y")

        result.update(
            {
                "respCode": constants.RESPONSE_CODE_OK,
                "groupNum": params.groupNum,
                "itemPickSeqNum": 1,
                "pickLineId": params.pickLineId,
                "productCode": params.productCode,
                "lotNumber": params.lotNumber,
                "effQty": params.effQty,
            }
        )
        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Set the quantity (Usf02) on the stock pack operation (lineId)
        Usf01 is the lot number.
        With the process "Parking" and "Reserve" the quantity (Usf02) can
        be more or less than the requested quantity. However Odoo
        doesn't allow to pick more than the requested quantity.
        It's why we check if the picked quantity is greater than the requested
        quantity. In this case, we look an error and we set the quantity
        to the requested quantity.

        If the param Usf03 (Zero Check) is filled we need to compare
        the virtual quantity in stock with the real (say by the picker)
        quantity in stock. If Usf03 is filled we have to stop to process
        and only check the quantity in stock.

        For the process Parking, if the stock if full, the picker will go to
        the reserve. In this case we need to split the pack operation
        (one operation for the stock and one operation for the reserve).

        For the process Reserve, if the stock if ull, the picker will return
        some quantity to the reserve. In this case we need to split the pack
        operation (one operation for the stock and one operation for the
        reserve). The operation for this reserve will have the same
        location for the source and the destination.
        :param params:
        :return:
        """
        line_id = params.lineId
        if not line_id:
            return

        if isinstance(line_id, int):
            line_id = str(line_id)

        line_id_list = line_id.split("_")
        if len(line_id_list) == 2:
            pack_operation_id = int(line_id_list[0])
            lot_id = int(line_id_list[1])
        else:
            pack_operation_id = int(line_id)
            lot_id = None

        pack_op = self.request.env["stock.pack.operation"].browse(pack_operation_id)
        if not len(pack_op):
            return

        try:
            # Retrieve the quantity
            real_qty = params.Usf02 and float(params.Usf02) or 0
            virtual_qty = self.check_picked_quantity(params, pack_op, real_qty)
            # and the lot number
            lot_number = params.Usf01

            lot = None
            if lot_number:
                if lot_id:
                    lot = self.request.env["stock.production.lot"].search(
                        [("id", "=", lot_id), ("voice_identifier", "=", lot_number)]
                    )

                if not lot:
                    lot = self.request.env["stock.production.lot"].search(
                        [
                            ("product_id", "=", pack_op.product_id.id),
                            ("voice_identifier", "=", lot_number),
                        ],
                        limit=1,
                    )

                if not lot:
                    error_message = "Pack op lot %s not found" % lot_number
                    _logger.error(error_message)
                    params.log(
                        picking_id=pack_op.picking_id.id,
                        operation_id=pack_operation_id,
                        exception=error_message,
                    )
                    return
                else:
                    lot_id = lot.id

            # If we receive a value for Usf03, it means that we have to
            # check if the available quantity (in Odoo) is the same than
            # the real quantity (say by the picker).
            actual_stock = params.Usf03
            if actual_stock and actual_stock.isdigit():
                actual_stock = int(actual_stock)
                self.check_actual_stock(params, pack_op, actual_stock, lot_id)
                return

            picking = pack_op.picking_id
            # The stock is full and the picker need to go to the reserve
            if (
                picking.picking_type_id.zetes_picking_type
                == constants.RANGEMENT_ASSIGNMENT
                and pack_op.zetes_state == constants.MOVE_FULL
            ) or (
                picking.picking_type_id.zetes_picking_type
                == constants.RANGEMENT_ASSIGNMENT
                and not virtual_qty
            ):
                reserve_rel_obj = self.request.env["pack.operation.reserve.rel"]
                reserve_rel = reserve_rel_obj.search(
                    [("pack_operation_id", "=", pack_op.id), ("lot_id", "=", lot_id)],
                    limit=1,
                    order="id DESC",
                )

                if not reserve_rel:
                    error_message = "Reserve not found for pack_op %s " "(lot %s)" % (
                        pack_op.id,
                        lot_id,
                    )
                    _logger.error(error_message)
                    params.log(
                        picking_id=pack_op.picking_id.id,
                        operation_id=pack_operation_id,
                        exception=error_message,
                    )
                    return

                reserve = reserve_rel.reserve_location_id
                pack_op.put_in_reserve(reserve.id)
            # Only for "Reserve". The stock is full and the picker will return
            # some quantity to the reserve
            elif (
                picking.picking_type_id.zetes_picking_type
                == constants.REASSORT_ASSIGNMENT
                and pack_op.product_qty > virtual_qty
            ):
                # Add the new quantity to the current pack op
                pack_op.add_qty(virtual_qty, lot_id)
                location_dest_id = pack_op.location_id.id
                new_qty = pack_op.product_qty - virtual_qty

                # Create the pack op for the quantity left in the reserve
                pack_op_move = pack_op.split_pack_op(new_qty, location_dest_id, lot_id)
                pack_op_move.add_qty(new_qty, lot_id)
            # Otherwise simple add the new quantity to the current pack op
            else:
                pack_op.add_qty(virtual_qty, lot_id)

        except Exception as e:
            self.rollback_to_savepoint()
            _logger.error(str(e))
            params.log(
                picking_id=pack_op.picking_id.id,
                operation_id=pack_operation_id,
                exception=e,
            )

    def check_actual_stock(self, params, pack_op, actual_stock, lot_id=None):
        """
        Check if the actual quantity in stock equals the available quantity
        in Odoo.
        :param params:
        :param pack_op:
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
        query_values = [pack_op.product_id.id, pack_op.location_id.id]

        self.request.env.cr.execute(available_qty_query, tuple(query_values))
        query_result = self.request.env.cr.fetchone()
        available_qty = query_result and query_result[0] or 0

        if available_qty != actual_stock:
            error_message = (
                "The theoretical stock (%s) is different"
                " from the actual stock (%s) for"
                " the product %s in the location %s"
                % (
                    available_qty,
                    actual_stock,
                    pack_op.product_id.display_name,
                    pack_op.location_id.display_name,
                )
            )
            if lot_id:
                lot = self.request.env["stock.production.lot"].browse(lot_id)
                error_message += " (lot %s)" % lot.name

            _logger.error(error_message)
            params.log(
                picking_id=pack_op.picking_id.id,
                operation_id=pack_op.id,
                exception=error_message,
                error_type="human",
            )

    def check_picked_quantity(self, params, pack_op, picked_quantity):
        """
        Zetes allows (only for Parking and Reserve) to take a quantity
        greater than the requested quantity. However Odoo refuse this case.
        If the picked quantity is greater than the requested quantity we need
        to virtually change the picked quantity with the requested quantity
        and send an email to warm the manager.
        :param pack_op:
        :param picked_quantity:
        :return:
        """
        total_picked_quantity = pack_op.qty_done + picked_quantity
        max_allowed_quantity = pack_op.product_qty

        if total_picked_quantity > max_allowed_quantity:
            error_message = (
                "The total picked quantity (%s) is greater than"
                " the requested quantity (%s) for the product "
                "%s (Operation ID %s)"
                % (
                    total_picked_quantity,
                    max_allowed_quantity,
                    pack_op.product_id.display_name,
                    pack_op.id,
                )
            )
            _logger.error(error_message)
            params.log(
                picking_id=pack_op.picking_id.id,
                operation_id=pack_op.id,
                exception=error_message,
                error_type="human",
            )
            return pack_op.product_qty - pack_op.qty_done

        return picked_quantity
