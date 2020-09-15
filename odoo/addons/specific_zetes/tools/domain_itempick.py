# -*- coding: utf-8 -*-
import logging

from domain_interface import DomainInterface, Parameters, Savepoint
from odoo import _

from .. import constants

_logger = logging.getLogger(__name__)


class Itempick(DomainInterface):
    EXAMPLE_REQU = (
        "208030828,2.2.3,3iV_101,REQU_ITEMPICK,30,1,20170207,"
        "072904,30427733118044,000000001625844,,,,1,"
        "0,,,,,,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208030828,2.2.3,3iV_101,RESP_ITEMPICK,30,1,20170207,"
        "072849,30427733118044,0,,000000001625844,,,,00001,"
        "00000000162584400001,1,1,,G,B,A,4,15,16,,,,,,,,,,"
        "000002,000000,00,Aucune indication,01,2520872,"
        "LAXANORM 100GR,,00006,0,,1,0,0,0,1,0,,pièce,,,,,,,,"
        "0,67709,00000,00000,00000,00000,,0016.65,,,"
    )
    EXAMPLE_RESU = (
        "208030828,2.2.3,3iV_101,RESU_ITEMPICK,30,1,20170207,"
        "072931,30427733121317,000000001625844,,,,1,"
        "00000000162584400001,,000002,000002,,"
        "01,0,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,"
    )
    REQU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "tripCounter",
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
        "tripCounter",
        "reqDestCarSeqNum",
        "reqDestCarSeqCD",
        "sourceLC1",
        "sourceLC2",
        "sourceLC3",
        "sourceLC4",
        "sourceLC5",
        "sourceLCCD",
        "sourceLCBarcode",
        "altSourceLC1",
        "altSourceLC2",
        "altSourceLC3",
        "altSourceLC4",
        "altSourceLC5",
        "altSourceLCCD",
        "altSourceLCBarcode",
        "lineIndicator",
        "reqQty",
        "effQty",
        "pickStatus",
        "promptInfo",
        "unitOfMeasure",
        "productCode",
        "productDescription",
        "productGroupCode",
        "productProperty1",
        "productProperty2",
        "productProperty3",
        "lessQtyAllowed",
        "moreQtyAllowed",
        "catchWeightFlag",
        "cycleCountFlag",
        "lotTrackingFlag",
        "expiryDateCheckFlag",
        "lotNumber",
        "UOMPrompt",
        "singlesInUOM",
        "minBlockCW",
        "maxBlockCW",
        "minAllowedCW",
        "maxAllowedCW",
        "expiryDate",
        "productBarcode",
        "scanProductBarcode",
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
        "itemPickSeqNum",
        "pickLineId",
        "lineIndicator",
        "reqQty",
        "effQtySourceLC",
        "effQtyAltSourceLC",
        "pickStatus",
        "tripCounter",
        "unitOfMeasure",
        "totalCatchWeight",
        "lotNumber",
        "productBarcode",
        "sourceLCBarcode",
        "altSourceLCBarcode",
        "effQtyDestCar01",
        "effQtyDestCar02",
        "effQtyDestCar03",
        "effQtyDestCar04",
        "effQtyDestCar05",
        "effQtyDestCar06",
        "effQtyDestCar07",
        "effQtyDestCar08",
        "effQtyDestCar09",
        "effQtyDestCar10",
        "effDestCarId01",
        "effDestCarId02",
        "effDestCarId03",
        "effDestCarId04",
        "effDestCarId05",
        "effDestCarId06",
        "effDestCarId07",
        "effDestCarId08",
        "effDestCarId09",
        "effDestCarId10",
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

    def requ(self, params):  # noqa: C901
        """
        Return a list of stock pack operation according the picking ID
        Param: groupNum (picking_id)
        :param params:
        :return:
        """
        # If there is no Picking ID we cannot assign a pack operation
        if not params.groupNum:
            result = Parameters(self, action="resp")
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": "No picking found",
                }
            )
            return result.format()

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

        # Cri01 define the order (01 => from the end to the start)
        if params.Cri01 == "1":
            order_by = "location_name DESC, id"
        else:
            order_by = "location_name ASC, id"

        print_price_query = """
        SELECT partner.is_price_on_labels,
               customer.is_b2c_customer
        FROM stock_picking AS picking
          INNER JOIN res_partner AS partner ON picking.partner_id = partner.id
          left JOIN res_partner AS customer ON picking.customer_id = customer.id
        WHERE picking.id = %s;
        """
        self.request.env.cr.execute(print_price_query, (picking_id,))
        print_price_result = self.request.env.cr.fetchone()
        is_print_price = False
        if print_price_result:
            is_price_on_labels, is_b2c_customer = print_price_result
            if is_price_on_labels and not is_b2c_customer:
                is_print_price = True

        # Check if we need to print on a portable printer
        is_portable_printer_result_query = """
        SELECT picking_type.is_portable_printer
        FROM stock_picking AS picking
          INNER JOIN stock_picking_type AS picking_type
          ON picking.picking_type_id = picking_type.id
        WHERE picking.id = %s"""
        self.request.env.cr.execute(is_portable_printer_result_query, (picking_id,))
        is_portable_printer_result = self.request.env.cr.fetchone()

        if is_portable_printer_result and is_portable_printer_result[0]:
            print_on_portable_printer = "1"
        else:
            print_on_portable_printer = "0"

        # In case of the lot is sold out (Usf06 == '04'), we need to add split
        # the pack op lot and reserve quantity in a new lot
        is_cut_itempick = False
        if params.Usf06 == constants.OP_CUT:
            is_cut_itempick = True
            line_id = params.Usf02
            if isinstance(line_id, int):
                line_id = str(line_id)

            line_id_list = line_id.split("_")
            if len(line_id_list) == 2:
                pack_operation_id = int(line_id_list[0])
                lot_id = int(line_id_list[1])
            else:
                pack_operation_id = int(line_id)
                lot_id = None

            picked_qty = int(params.Usf04 or 0)

            pack_op = self.request.env["stock.pack.operation"].browse(pack_operation_id)
            # Check if the product is tracked or not
            product = pack_op.product_id
            if product.tracking != "none":
                # Retrieve the pack lot
                pack_lot = self.request.env["stock.pack.operation.lot"].search(
                    [("operation_id", "=", pack_operation_id), ("lot_id", "=", lot_id)],
                    limit=1,
                )
                if not pack_lot:
                    result = Parameters(self, action="resp")
                    result.update(
                        {
                            "respCode": constants.RESPONSE_CODE_ERROR,
                            "respMsg": "Lot pack operation not found",
                        }
                    )
                    return result.format()

                # Add the picked quantity on the pack lot
                pack_op.add_qty(picked_qty, pack_lot.lot_id.id)

                msg = u"Out of stock for lot {} (product {}): {} taken".format(
                    pack_lot.lot_id.name, pack_op.product_id.name, picked_qty
                )
            else:
                pack_lot = None
                # Add the picked quantity on the pack operation
                pack_op.add_qty(picked_qty)

                msg = u"Out of stock (product {}): {} taken".format(
                    pack_op.product_id.name, picked_qty
                )
            params.log(
                picking_id=picking_id,
                operation_id=pack_operation_id,
                exception=msg,
                error_type="human",
            )

            with Savepoint(self.request.env.cr) as lot_savepoint:
                try:
                    # Call the method to skip this operation
                    pack_op._skip_operation(
                        pack_op_lot_id=pack_lot, raise_if_nothing_to_block=False
                    )
                except Exception as e:
                    lot_savepoint.rollback()
                    _logger.error(str(e))
                    # we can't return an error at this stage of the process
                    # otherwise zetes/ the operator could resend the same request
                    # and since this code block is into a savepoint all the
                    # data are already stored into the DB (no rollback of the
                    # modifications done before this code block)

        # Search all pack operations for this picking
        lines = self.request.env["stock.pack.operation"].search(
            [
                ("picking_id", "=", picking_id),
                ("location_id.is_valid_location", "=", True),
                ("zetes_state", "in", [constants.OP_DEFAULT, constants.OP_SKIPPED]),
            ],
            order=order_by,
        )

        # Filter lines
        # We want only operation with a quantity to to done different
        # than the quantity done.
        lines = lines.filtered(lambda line: int(line.qty_done) < int(line.product_qty))
        split_lines = lines.split_pack_op_lines()

        sequence = 1
        result = []

        if not split_lines:
            error_message = _("There is no lines for the picking %s") % picking_id

            params.log(picking_id=picking_id, exception=error_message)

            # If a cut return no lines, we need to return the code 11
            # (no lines available) and not the code 10 (error)
            if is_cut_itempick:
                resp_code = constants.RESPONSE_CODE_NO_LINES
                error_message = None
            else:
                resp_code = constants.RESPONSE_CODE_ERROR

            result = Parameters(self, action="resp")
            result.update({"respCode": resp_code, "respMsg": error_message})
            return result.format()

        for line, pack_lot in split_lines:
            if pack_lot:
                qty_to_do = pack_lot.qty_todo
                qty_done = pack_lot.qty
            else:
                qty_to_do = line.product_qty
                qty_done = line.qty_done

            if pack_lot:
                line_id = "{}_{}".format(line.id, pack_lot.lot_id.id)
            else:
                line_id = line.id

            line_values = Parameters(self)
            line_values.update(
                {
                    "respCode": constants.RESPONSE_CODE_OK,
                    "groupNum": picking_id,
                    "pickLineId": line_id,
                    "reqDestCarSeqNum": 1,
                    "reqQty": format(int(qty_to_do), "0%d" % 6),
                    "effQty": format(int(qty_done), "0%d" % 6),
                    "pickStatus": line.zetes_state,
                    "tripCounter": 1,
                }
            )

            product = line.product_id

            line_values.update(
                {
                    "productCode": product.default_code,
                    "productDescription": product.name,
                    "productProperty1": None,
                    "productProperty2": print_on_portable_printer,
                    "lessQtyAllowed": 1,  # Constant value
                    "moreQtyAllowed": 0,  # Constant value
                    "catchWeightFlag": 0,  # Constant value
                    "expiryDateCheckFlag": 0,  # Constant value
                    "productBarcode": product.barcode,
                    "scanProductBarcode": 0,  # Constant value
                    "UOMPrompt": line.product_uom_id.name,
                    "itemPickSeqNum": sequence,
                }
            )

            if is_print_price:
                line_values.Usf07 = line.product_id.indicated_price

            if product.tracking == "lot":
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
                line_values.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Location not found for the product %s")
                        % product.name,
                    }
                )
                result.append(line_values)
                continue

            # TODO Please remove me later (when dynamic locations will removed)
            shelf_source = location.shelf
            if len(str(shelf_source)) == 1:
                shelf_source = "0%s" % shelf_source

            # Set coordonates location of the bin
            line_values.update(
                {
                    "sourceLC1": location.zone,
                    "sourceLC2": location.corridor,
                    "sourceLC3": shelf_source,
                    "sourceLC4": location.height,
                    "sourceLC5": location.box,
                    "sourceLCCD": location.get_checksum(),
                }
            )

            if pack_lot and pack_lot.lot_id:
                lot = pack_lot.lot_id
                line_values.update(
                    {
                        "Usf01": lot.voice_identifier or lot.name[-3:],
                        "Usf02": lot.checksum,
                    }
                )

            # # If the available quantity for this location is less than
            # # the zero check limit, it means that we have to ask
            # # a zero check.
            # available_qty_query = """
            # SELECT sum(quant.qty)
            # FROM stock_quant AS quant
            # WHERE quant.product_id = %s
            # AND quant.location_id = %s
            # AND quant.reservation_id IS NULL
            # """
            # self.request.env.cr.execute(available_qty_query,
            #                             (line.product_id.id,
            #                              line.location_id.id))
            # query_result = self.request.env.cr.fetchone()
            # available_qty = query_result and query_result[0] or 0
            #
            # forcast_available_qty = available_qty - line.product_qty
            # if forcast_available_qty <= constants.ZERO_CHECK_LIMIT:
            #     line_values.cycleCountFlag = 1
            # else:
            #     line_values.cycleCountFlag = 0

            # TODO Review the zero check
            line_values.cycleCountFlag = 0

            result.append(line_values)
            sequence += 1

        return "\n".join([line.format() for line in result])

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

        line_id = params.pickLineId

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
            status = params.pickStatus
            if status:
                pack_op.write({"zetes_state": status})

                # If status == OP_CANCELED => remove all actions for this line
                if status == constants.OP_CANCELED:
                    if lot_id:
                        pack_lot = pack_op.pack_lot_ids.filtered(
                            lambda line: line.lot_id.id == lot_id
                        )
                        pack_lot.qty = 0
                        pack_op.save()
                    else:
                        pack_op.qty_done = 0

        except Exception as e:
            self.rollback_to_savepoint()
            _logger.error(str(e))
            params.log(
                picking_id=pack_op.picking_id.id,
                operation_id=pack_operation_id,
                exception=e,
            )
