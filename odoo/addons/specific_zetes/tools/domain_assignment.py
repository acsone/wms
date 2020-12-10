# -*- coding: utf-8 -*-
import logging
from datetime import date

from domain_interface import DomainInterface, Parameters
from odoo import _

from .. import constants

_logger = logging.getLogger(__name__)

MAX_RETRY = 10


class Assignment(DomainInterface):
    EXAMPLE_REQU = (
        "208030828,2.2.3,3iV_101,REQU_ASSIGNMENT,30,1,20170207,"
        "072835,30427733115352,1,1,1,01,,,,,,,,,,,,,,,,,,,,,,,,,"
        ",,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208030828,2.2.3,3iV_101,RESP_ASSIGNMENT,30,1,20170207,"
        "072820,30427733115352,0,,1,1,000000001625844,,00,,"
        "Vétérinaires,95,0,0,C,CLINIQUE VET. DU MONT-FALISE,"
        "4520 WANZE,00018,"
    )
    EXAMPLE_RESU = (
        "208030828,2.2.3,3iV_101,RESU_ASSIGNMENT,30,1,20170207,"
        "072836,30427733115363,000000001625844,,,,"
        "01,123456789,,,,,,,,,,"
    )
    REQU = (
        "assignmentType",
        "requestType",
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
        "Cri11",
        "Cri12",
        "Cri13",
        "Cri14",
        "Cri15",
        "Cri16",
        "Cri17",
        "Cri18",
        "Cri19",
        "Cri20",
        "Cri21",
        "Cri22",
        "Cri23",
        "Cri24",
        "Cri25",
        "Cri26",
        "Cri27",
        "Cri28",
        "Cri29",
        "Cri30",
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
        "assignmentType",
        "responseType",
        "groupNum",
        "groupSubNum",
        "assignmentStatus",
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
        "Usf11",  # FOR chronovet customer
    )
    RESU = (
        "groupNum",
        "groupSubNum",
        "headerNum",
        "headerSubNum",
        "assignmentStatus",
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
        Return a picking to the picker according several rules:
        - If the picker want to start a new picking (Cri02 is empty) or if
        the picker continue a picking (Cri02 will contain the picking ID)
        - The location can be defined with Cri01
        - If requestType equals 0, it means that we are looking for a picking
        with an operator. If the requestType equals, it means that we want
        a picking without an operator
        :param params:
        :return:
        """
        result = Parameters(self, action="resp")

        # If the picker request a new picking (Cri02 is the picking ID)
        if not params.Cri02:
            assignment_type = params.assignmentType
            # Search for a standard picking
            if assignment_type == constants.PICKING_ASSIGNMENT:
                picking = self.get_picking(params)
                result.assignmentType = constants.PICKING_ASSIGNMENT
            # Search for a picking assignment
            elif assignment_type == constants.RANGEMENT_ASSIGNMENT:
                picking = self.get_picking_parking(params)
                result.assignmentType = constants.RANGEMENT_ASSIGNMENT
            # Search for a picking in reserve
            elif assignment_type == constants.REASSORT_ASSIGNMENT:
                picking = self.get_picking_reserve(params)
                result.assignmentType = constants.REASSORT_ASSIGNMENT
            else:
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Unknown assignment type"),
                    }
                )
                return result.format()

            if not picking:
                result.update(
                    {
                        "respCode": constants.RESPONSE_CODE_ERROR,
                        "respMsg": _("Cannot found a picking"),
                    }
                )
                return result.format()
        # If the picker want to continue a picking (Cri02 is not empty)
        else:
            picking_id = int(params.Cri02)
            picking = self.env["stock.picking"].browse(picking_id)

        # Assign the picking
        picking.assign_operator()

        # There are two bin checksum on location
        # According the day of the month, the picking have to use the "Right"
        # or "Left" checkum. For the even day, the picking take the checksum
        # on the right (=> bin_checksum_1) and for the odoo day, the picker
        # take the checksum on the left (=> bin_checksum_2)
        is_odd_day = date.today().day % 2
        if is_odd_day:
            result.Usf10 = _("left")
        else:
            result.Usf10 = _("right")

        partner = picking.partner_id
        customer = picking.customer_id
        customer_name = ""
        address = u"{} {}".format(partner.zip or "", partner.city or "")
        if customer.is_b2c_customer:
            customer_name = customer.name
            address = u"{} -- {}".format(address, customer_name)

        round_name = picking.sudo().delivery_round_id.template_id.code

        result.update(
            {
                "respCode": constants.RESPONSE_CODE_OK,
                "groupNum": picking.id,
                "Usf02": partner.alcyon_category_id.name,
                "Usf03": round_name,
                "Usf04": 0,  # Constant value
                "Usf05": 0,  # Constant value
                "Usf07": partner.name,  # Partner name
                # Zip + city
                "Usf08": address,
                "Usf09": picking.nbr_actions,  # Nbr of operation
                "Usf11": customer_name,
            }
        )

        is_passport_required = (
            picking.picking_type_id.passport and partner.is_passport_required
        )
        picking.is_passport_required = is_passport_required
        if is_passport_required:
            result.Usf06 = "C"  # This partner request a double control
            picking.assign_picking_checksum()
        else:
            result.Usf06 = "E"  # Simple packaging

        if picking.zetes_state == constants.AS_CANCELED:
            result.update(
                {"assignmentStatus": constants.AS_START, "Usf01": picking.checksum}
            )
        else:
            result.assignmentStatus = constants.AS_DEFAULT

        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        Set the picking state (field zetes_state) according assignmentStatus
        assignmentStatus is a number (see below).
        State:
        01/02: The operator start the picking.
                         We assign this picking to the operator.
        04/08: The operator has completed the picking
                        and the picking must be validated.
        05: The operator interrupts the picking. The picking is released
                        and we assign a checksum for this picking.
        :param params:
        :return:
        """
        picking_id = params.groupNum
        if not picking_id:
            return

        picking = self.env["stock.picking"].browse(int(picking_id))
        if not len(picking):
            return
        picking._lock_rows()
        try:
            picking_zetes_state = params.assignmentStatus

            if params.assignmentStatus in [constants.AS_DONE, constants.AS_FINISHED]:

                if not picking.is_passport_required:
                    picking.validate_picking()
                else:
                    picking_zetes_state = "passport"
            elif params.assignmentStatus == constants.AS_CANCELED:
                picking.interrupt_picking()

            picking.zetes_state = picking_zetes_state
        except Exception as e:
            self.rollback_to_savepoint()
            _logger.exception(str(e))
            params.log(picking_id=picking_id, exception=e)

    def get_picking(self, params):
        """
        Return a standard picking
        :param params:
        :return:
        """
        picking_query = """
SELECT picking.id
FROM stock_picking AS picking
  INNER JOIN stock_picking_type AS pick_type
    ON picking.picking_type_id = pick_type.id
  LEFT JOIN picking_zone ON pick_type.picking_zone_id = picking_zone.id
  INNER JOIN round_instance AS round
    ON picking.delivery_round_id = round.id
WHERE picking.picking_type_subcode = 'PICK'
      AND picking.state IN ('partially_available', 'assigned')
      AND pick_type.zetes_picking_type = %(picking_type)s
      AND EXISTS(SELECT 1
                 FROM stock_pack_operation AS operation
                 INNER JOIN stock_location l
                   ON operation.location_id = l.id
                 WHERE operation.picking_id = picking.id
                 AND operation.zetes_state in %(op_zetes_state)s
                 AND l.is_valid_location
                 )
      AND round.state in ('draft', 'pending', 'close')
      AND (
            (
                picking.operator_id IS NULL
                AND round.picking_launched
                AND picking.zetes_state IN %(picking_zetes_states_no_operator)s
            )
           OR
           (
                picking.operator_id = %(operator)s
                AND picking.zetes_state NOT IN %(picking_zetes_states_operator)s
           )
      )
--      AND NOT EXISTS (SELECT 1
--                      FROM stock_pack_operation AS operation
--                        INNER JOIN stock_inventory_line AS sil
--                           ON sil.product_id = operation.product_id
--                         INNER JOIN stock_inventory AS si
--                           ON sil.inventory_id = si.id
--                       WHERE operation.picking_id = picking.id
--                       AND si.state = 'confirm')
                """
        query_values = {
            "picking_type": constants.PICKING_ASSIGNMENT,
            "op_zetes_state": (constants.OP_DEFAULT, constants.OP_SKIPPED),
            "operator": self._operator_user.id,
            "picking_zetes_states_no_operator": (
                constants.AS_DEFAULT,
                constants.AS_CANCELED,
            ),
            "picking_zetes_states_operator": (
                constants.AS_DONE,
                constants.AS_FINISHED,
                "passport",
                "done",
            ),
        }

        # Search a picking in a specific zone (like Food)
        zone_code = params.Cri01
        if zone_code:
            picking_query += "AND picking_zone.code = %(zone_code)s "
            query_values["zone_code"] = zone_code

        picking_query += (
            "ORDER BY picking.operator_id, "
            "round.date, "
            "round.time_picking_planned, "
            "picking.rank DESC "
            "LIMIT 1 "
            "FOR UPDATE OF picking SKIP LOCKED;"
        )
        self.env.cr.execute(picking_query, query_values)
        query_result = self.env.cr.fetchone()

        if query_result and query_result[0]:
            picking_id = query_result[0]
            picking = self.env["stock.picking"].browse(picking_id)
        else:
            return False

        return picking

    def get_picking_parking(self, params):
        """
        Return a picking from the parking.
        First the method will search for an existing picking.
        Otherwise the method will search in the report Parking and create
        a new picking.
        :param params:
        :return:
        """

        picking_query = """
SELECT picking.id
FROM stock_picking AS picking
  INNER JOIN stock_picking_type AS pick_type
    ON picking.picking_type_id = pick_type.id
  LEFT JOIN picking_zone ON pick_type.picking_zone_id = picking_zone.id
WHERE picking.state IN ('partially_available', 'assigned')
  AND picking.zetes_state IN %(picking_zetes_state)s
  AND pick_type.zetes_picking_type = %(picking_type)s
  AND EXISTS(SELECT 1
             FROM stock_pack_operation AS operation
             INNER JOIN stock_location l
               ON operation.location_dest_id = l.id
             WHERE operation.picking_id = picking.id
             AND operation.zetes_state in %(op_zetes_state)s
             AND l.is_valid_location
             )
  AND (picking.operator_id IS NULL OR picking.operator_id = %(operator)s)
--  AND NOT EXISTS (SELECT 1
--                  FROM stock_pack_operation AS operation
--                    INNER JOIN stock_inventory_line AS sil
--                      ON sil.product_id = operation.product_id
--                    INNER JOIN stock_inventory AS si
--                      ON sil.inventory_id = si.id
--                  WHERE operation.picking_id = picking.id
--                  AND si.state = 'confirm')
                """

        query_values = {
            "picking_zetes_state": (constants.AS_DEFAULT, constants.AS_CANCELED),
            "picking_type": constants.RANGEMENT_ASSIGNMENT,
            "op_zetes_state": (constants.OP_DEFAULT, constants.OP_SKIPPED),
            "operator": self._operator_user.id,
        }

        # Search a picking in a specific zone (like Food)
        zone_code = params.Cri01
        if zone_code:
            picking_query += "AND picking_zone.code = %(zone_code)s "
            query_values["zone_code"] = zone_code

        picking_query += (
            "ORDER BY picking.operator_id, " "picking.rank DESC " "LIMIT 1;"
        )

        self.env.cr.execute(picking_query, query_values)
        query_result = self.env.cr.fetchone()

        if query_result and query_result[0]:
            picking_id = query_result[0]
            picking = self.env["stock.picking"].browse(picking_id)
            return picking

        # Picking not found. Try to create a new one.
        zone_code = params.Cri01
        zone_condition = ""
        query_values = {}
        if zone_code:
            zone_condition = "AND picking_zone.code = %(zone_code)s"
            query_values["zone_code"] = zone_code

        report_query = (
            """
          SELECT report.id
          FROM report_stock_refill_arrange AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
          LEFT JOIN picking_zone
            ON stock_location.picking_zone_id = picking_zone.id
          WHERE
          -- NOT EXISTS (SELECT 1
          --   FROM stock_inventory_line AS sil
          --     INNER JOIN stock_inventory AS si
          --       ON sil.inventory_id = si.id
          --   WHERE si.state = 'confirm'
          --   AND sil.location_id = report.location_id)
          -- AND
            report.reservation_id IS NULL
            %s
          LIMIT 1
        """
            % zone_condition
        )

        counter = 0
        while counter < MAX_RETRY:
            self.env.cr.execute(report_query, query_values)
            report_id = self.env.cr.fetchone()
            if not report_id:
                break

            report_id = report_id[0]

            model_name = "report.stock.refill.arrange"
            report = self.env[model_name].browse(report_id)
            # Create the picking
            picking = report.create_picking()
            is_valid_location = True
            for pack_op in picking.pack_operation_product_ids:
                if (
                    not pack_op.location_dest_id.zone
                    or not pack_op.location_dest_id.corridor
                ):
                    is_valid_location = False
                    break

            if is_valid_location:
                return picking
            else:
                error_message = (
                    "The picking %s contains one or more "
                    "invalid location" % picking.display_name
                )
                _logger.error(error_message)
                params.log(picking_id=picking.id, exception=error_message)

            counter += 1

        return False

    def get_picking_reserve(self, params):
        """
        Return a picking from the reserve.
        First the method will search for an existing picking.
        Otherwise the method will search in the report reserve and create
        a new picking.
        :param params:
        :return:
        """
        # Search for an existing picking
        picking_query = """
SELECT picking.id
FROM stock_picking AS picking
  INNER JOIN stock_picking_type AS pick_type
    ON picking.picking_type_id = pick_type.id
  LEFT JOIN picking_zone ON pick_type.picking_zone_id = picking_zone.id
WHERE picking.state IN ('partially_available', 'assigned')
  AND picking.zetes_state IN %(picking_zetes_state)s
  AND pick_type.zetes_picking_type = %(picking_type)s
  AND EXISTS(SELECT 1
             FROM stock_pack_operation AS operation
             INNER JOIN stock_location l
               ON operation.location_dest_id = l.id
             WHERE operation.picking_id = picking.id
             AND operation.zetes_state in %(op_zetes_state)s
             AND l.is_valid_location
             )
  AND (picking.operator_id IS NULL OR picking.operator_id = %(operator)s)
--  AND NOT EXISTS (SELECT 1
--                  FROM stock_pack_operation AS operation
--                    INNER JOIN stock_inventory_line AS sil
--                      ON sil.product_id = operation.product_id
--                    INNER JOIN stock_inventory AS si
--                      ON sil.inventory_id = si.id
--                  WHERE operation.picking_id = picking.id
--                  AND si.state = 'confirm')
                """

        query_values = {
            "picking_zetes_state": (constants.AS_DEFAULT, constants.AS_CANCELED),
            "picking_type": constants.REASSORT_ASSIGNMENT,
            "op_zetes_state": (constants.OP_DEFAULT, constants.OP_SKIPPED),
            "operator": self._operator_user.id,
        }

        # Search a picking in a specific zone (like Food)
        zone_code = params.Cri01
        if zone_code:
            picking_query += "AND picking_zone.code = %(zone_code)s "
            query_values["zone_code"] = zone_code

        picking_query += (
            "ORDER BY picking.operator_id, " "picking.rank DESC " "LIMIT 1;"
        )

        self.env.cr.execute(picking_query, query_values)
        query_result = self.env.cr.fetchone()

        if query_result and query_result[0]:
            picking_id = query_result[0]
            picking = self.env["stock.picking"].browse(picking_id)
            return picking

        # Picking not found. Try to create a new one.
        zone_code = params.Cri01
        zone_condition = ""
        query_values = {}
        if zone_code:
            zone_condition = "AND picking_zone.code = %(zone_code)s"
            query_values["zone_code"] = zone_code

        report_query = (
            """
          SELECT report.id
          FROM report_stock_refill_reassort AS report
          LEFT JOIN stock_location ON stock_location.id = report.location_id
          LEFT JOIN picking_zone
            ON stock_location.picking_zone_id = picking_zone.id
          WHERE
          -- NOT EXISTS (SELECT 1
          --   FROM stock_inventory_line AS sil
          --     INNER JOIN stock_inventory AS si
          --       ON sil.inventory_id = si.id
          --   WHERE si.state = 'confirm'
          --   AND sil.product_id = report.product_id)
            report.reservation_id IS NULL
            %s
          LIMIT 1;
        """
            % zone_condition
        )

        counter = 0
        while counter < MAX_RETRY:
            self.env.cr.execute(report_query, query_values)
            report_id = self.env.cr.fetchone()
            if not report_id:
                break
            report_id = report_id[0]

            model_name = "report.stock.refill.reassort"
            report = self.env[model_name].browse(report_id)

            # Create the picking
            picking = report.create_picking()
            is_valid_location = True
            for pack_op in picking.pack_operation_product_ids:
                if not pack_op.location_dest_id.is_valid_location:
                    is_valid_location = False
                    break

            if is_valid_location:
                return picking
            else:
                error_message = (
                    "The picking %s contains one or more "
                    "invalid location" % picking.display_name
                )
                _logger.error(error_message)
                params.log(picking_id=picking.id, exception=error_message)

        return False
