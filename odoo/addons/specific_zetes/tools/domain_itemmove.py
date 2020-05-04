# -*- coding: utf-8 -*-
import logging

from domain_interface import DomainInterface, Parameters
from odoo import _

from .. import constants

_logger = logging.getLogger(__name__)


class Itemmove(DomainInterface):
    EXAMPLE_REQU = (
        "200294543,2.2.3,3iV_101,REQU_ITEMMOVE,02,1,20171120,"
        "102754,02430594358406,2,,,,1,123456789,,,,,,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "200294543,2.2.3,3iV_101,RESP_ITEMMOVE,02,1,20171120,"
        "102839,02430594364298,0,,2,,,,1,0,1,2,,,,,,,,,,,,,,,"
        "000100,000000,,,,1799881,ADERMA EXOMEGA HUILE DOUCHE "
        "500ml,,,,,,0,179,,,,,,,,,"
    )
    EXAMPLE_RESU = (
        "200294543,2.2.3,3iV_101,RESU_ItemMove,02,1,20171120,"
        "113111,02430594800116,6,,,,1,4,,000002,000020,01,"
        ",,,,,,,,,0,,,,,,,,,,,,,,,,,,,"
    )
    REQU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "itemMoveType",
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
        "itemMoveSeqNum",
        "moveLineId",
        "itemMoveType",
        "sourceLC1",
        "sourceLC2",
        "sourceLC3",
        "sourceLC4",
        "sourceLC5",
        "sourceLCCD",
        "sourceLCBarcode",
        "destLC1",
        "destLC2",
        "destLC3",
        "destLC4",
        "destLC5",
        "destLCCD",
        "destLCBarcode",
        "lineIndicator",
        "reqQty",
        "effQty",
        "moveStatus",
        "promptInfo",
        "unitOfMeasure",
        "productCode",
        "productDescription",
        "productGroupCode",
        "productProperty1",
        "productProperty2",
        "productProperty3",
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
        "itemMoveSeqNum",
        "moveLineId",
        "lineIndicator",
        "itemMoveType",
        "quantity",
        "moveStatus",
        "unitOfMeasure",
        "lotNumber",
        "sourceLC1",
        "sourceLC2",
        "sourceLC3",
        "sourceLC4",
        "sourceLC5",
        "sourceLCCD",
        "sourceLCBarcode",
        "destLCPresentFlag",
        "destLC1",
        "destLC2",
        "destLC3",
        "destLC4",
        "destLC5",
        "destLCCD",
        "destLCBarcode",
        "productBarcode",
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

        # If there is no Picking ID we cannot assign a pack operation
        if not params.groupNum:
            result = Parameters(self, action="resp")
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("No picking found"),
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

        if params.itemMoveType == constants.MOVE_TYPE_LOAD:
            lines = self.get_load_lines(params, picking_id)
        elif params.itemMoveType == constants.MOVE_TYPE_PUT:
            lines = self.get_put_lines(params, picking_id)
        else:
            _logger.error("itemMoveType %s unknown" % params.itemMoveType)
            lines = []

        if not lines:
            error_message = _("There is no lines for the picking %s") % picking_id

            params.log(picking_id=picking_id, exception=error_message)

            result = Parameters(self, action="resp")
            result.update(
                {"respCode": constants.RESPONSE_CODE_ERROR, "respMsg": error_message}
            )
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
                # REQU_ITEMMOVE will return a list of move by product AND
                # by lot. In some case we need to know on which lot we are
                # working.
                if lot:
                    line_id = "{}_{}".format(line.id, lot.id)
                else:
                    line_id = line.id

            # TODO Please remove me later (when dynamic locations will removed)
            shelf_source = location.shelf
            if len(str(shelf_source)) == 1:
                shelf_source = "0%s" % shelf_source

            if params.itemMoveType == constants.MOVE_TYPE_LOAD:
                sourceLC1 = u"{}{}{}{}".format(
                    location.corridor, shelf_source, location.height, location.box
                )
            else:
                sourceLC1 = location.zone

            line_values.update(
                {
                    "moveStatus": constants.MOVE_DEFAULT,
                    "respCode": constants.RESPONSE_CODE_OK,
                    "groupNum": picking_id,
                    "moveLineId": line_id,
                    "itemMoveSeqNum": sequence,
                    "itemMoveType": move_type,
                    "reqQty": format(int(qty), "0%d" % 6),
                    "effQty": format(int(line.qty_done), "0%d" % 6),
                    "productCode": product.default_code,
                    "productDescription": product.name,
                    "productBarcode": product.barcode,
                    "scanProductBarcode": 0,  # Constant value
                    "sourceLC1": sourceLC1,
                    "sourceLC2": location.corridor,
                    "sourceLC3": shelf_source,
                    "sourceLC4": location.height,
                    "sourceLC5": location.box,
                    "sourceLCCD": location.get_checksum(),
                }
            )

            # TODO Please remove me later (when dynamic locations will removed)
            shelf_dest = location_dest_id.shelf
            if len(str(shelf_dest)) == 1:
                shelf_dest = "0%s" % shelf_dest

            # If it is a reserved quantity the location destination
            # is the same than the current location
            if move_type == constants.MOVE_TYPE_LOAD:
                line_values.update(
                    {
                        "destLC1": location_dest_id.zone,
                        "destLC2": location_dest_id.corridor,
                        "destLC3": shelf_dest,
                        "destLC4": location_dest_id.height,
                        "destLC5": location_dest_id.box,
                        "destLCCD": location_dest_id.get_checksum(),
                    }
                )

            if line.zetes_state == constants.MOVE_FULL:
                line_values.update(
                    {
                        "destLC3": None,
                        "destLC4": None,
                        "destLC5": None,
                        "destLCCD": None,
                    }
                )

            if lot:
                line_values.Usf01 = lot.checksum
                line_values.Usf03 = lot.voice_identifier
            else:
                line_values.Usf01 = product.default_code[-3:]
                line_values.Usf03 = product.default_code[:3]

            # Set the type of load (load or unload) move type "Load"
            if move_type == constants.MOVE_TYPE_LOAD:
                line_values.Usf02 = load_or_unload

            result.append(line_values)
            sequence += 1

        return "\n".join([line.format() for line in result])

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Change the state of the current stock pack operation (moveLineId)

        This method will validate the picking for the process Reserve (Zetes
        doesn't send a RESU_ASSIGNMENT for the process Reserve)
        :param params:
        :return:
        """
        line_id = params.moveLineId
        if not line_id:
            return

        if isinstance(line_id, int):
            line_id = str(line_id)

        pack_operation_id = int(line_id.split("_")[0])

        pack_op = self.request.env["stock.pack.operation"].browse(pack_operation_id)
        if not len(pack_op):
            return

        try:
            status = params.moveStatus
            if status:
                pack_op.write({"zetes_state": status})

                # For a picking from the reserve (itemMoveType = MOVE_TYPE_PUT)
                # Zetes doesn't send a RESU_ASSIGNMENT with the status
                # done. It means that we have to validate the picking
                # in any case.
                if params.itemMoveType == constants.MOVE_TYPE_PUT:
                    pack_op.picking_id.validate_picking()

        except Exception as e:
            self.rollback_to_savepoint()
            _logger.error(str(e))
            params.log(
                picking_id=pack_op.picking_id.id,
                operation_id=pack_operation_id,
                exception=e,
            )

    def get_load_lines(self, params, picking_id):
        """
        Return a list of lines for the process Parking
        :param params:
        :param picking_id:
        :return:
        """

        # Cri01 define the order (01 => from the end to the start)
        if params.Cri01 == "1":
            order_by = "location_dest_name DESC"
        else:
            order_by = "location_dest_name ASC"

        # Search all pack operations for this picking
        # The state of the line must be
        # "MOVE_DEFAULT", "MOVE_SKIPPED" or "MOVE_FULL"
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

        # FIXME - Check remaining qty after rangement is enough for
        # filling the reservation
        reserved_quants_query = """
        SELECT quant.lot_id, SUM(quant.qty)
        FROM stock_quant AS quant
        WHERE quant.location_id = %s
        AND quant.product_id = %s
        AND quant.reservation_id IS NOT NULL
        AND quant.reservation_id NOT IN (
          SELECT move.id FROM stock_move AS move WHERE move.picking_id = %s)
        GROUP BY quant.lot_id;
        """

        production_lot_obj = self.request.env["stock.production.lot"]
        reserved_lines = []
        put_away_lines = []
        for line in lines:
            self.request.env.cr.execute(
                reserved_quants_query,
                (line.location_id.id, line.product_id.id, picking_id),
            )
            query_result = self.request.env.cr.fetchall()
            for quant in query_result:
                lot = production_lot_obj.browse(quant[0])
                reserved_lines.append((line, lot, quant[1], constants.MOVE_UNLOAD))

            if not line.pack_lot_ids:
                put_away_lines.append(
                    (line, None, line.product_qty, constants.MOVE_LOAD)
                )
            else:
                pack_lots = line.pack_lot_ids.filtered(
                    lambda lot: lot.qty < lot.qty_todo
                )
                for pack_lot in pack_lots:
                    if pack_lot.qty_todo:
                        put_away_lines.append(
                            (
                                line,
                                pack_lot.lot_id,
                                pack_lot.qty_todo,
                                constants.MOVE_LOAD,
                            )
                        )

        return reserved_lines + put_away_lines

    def get_put_lines(self, params, picking_id):
        """
        Return a list with only one line for the process Reserve
        :param params:
        :param picking_id:
        :return:
        """
        # Search ONLY ONE pack operations for this picking
        # The state of this line must be
        # "MOVE_DEFAULT" or "MOVE_SKIPPED"
        lines = self.request.env["stock.pack.operation"].search(
            [
                ("picking_id", "=", picking_id),
                ("zetes_state", "in", [constants.MOVE_DEFAULT, constants.MOVE_SKIPPED]),
            ]
        )

        # Filter line
        # We want only operation with a quantity to to done different
        # than the quantity done.
        lines = lines.filtered(lambda x: int(x.qty_done) != int(x.product_qty))

        if not lines:
            return []

        # Take the first line
        line = lines[0]
        if not line.pack_lot_ids:
            return [[line, None, line.product_qty, None]]

        pack_lots = line.pack_lot_ids.filtered(lambda lot: lot.qty < lot.qty_todo)
        if not pack_lots:
            _logger.error(
                "Error with the line %s (picking %s):\n"
                "No valid lots" % (line.id, picking_id)
            )
            return []
        pack_lot = pack_lots[0]

        return [[line, pack_lot.lot_id, pack_lot.qty_todo, None]]
