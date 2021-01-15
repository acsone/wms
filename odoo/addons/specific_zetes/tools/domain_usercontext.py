# -*- coding: utf-8 -*-
from domain_interface import DomainInterface, Parameters

from odoo import _

from .. import constants


class Usercontext(DomainInterface):
    EXAMPLE_REQU = (
        "208030824,2.2.3,3iV_101,REQU_USERCONTEXT,98,1,20170207,"
        "072932,98427733121320,1,,01,,,,,,,,,,,,,,,,"
    )
    EXAMPLE_RESP = (
        "208030824,2.2.3,3iV_101,RESP_USERCONTEXT,98,1,"
        "20170207,072758,98427733121320,0,,1,01,,1,"
        "Serge Diplo,,0,,,,,,,,,,"
    )
    EXAMPLE_RESU = (
        "208092662,2.2.3,3iV_101,RESU_USERCONTEXT,87,1,20170207,"
        "081534,874277334413394,4,70,,1,Monica Checchi,,,,,,,,,,,,"
    )
    REQU = (
        "contextType",
        "requestType",
        "scenarioStatus",
        "Cri01",
        "Cri02",
        "Cri03",
        "Cri04",
        "Cri05",
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
        "contextType",
        "scenarioStatus",
        "responseType",
        "assignmentType",
        "operName",
        "operType",
        "unitSlam",
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
        "contextType",
        "scenarioStatus",
        "requestType",
        "assignmentType",
        "operName",
        "operType",
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
        Return information about the picker (a picker is a res.user).
        The code of the picker is send in the header
        (treat by the _init_ of DomainInterface).
        It's why we already have the attribute self._operator_user with the
        picker.
        :param params:
        :return:
        """
        result = Parameters(self, action="resp")

        if not self._operator_user:
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("User not found"),
                }
            )

            return result.format()

        # The picker (zetes user) must have the group "warehouse"
        user = self.env.user
        if not user.has_group("stock.group_stock_user"):
            result.update(
                {
                    "respCode": constants.RESPONSE_CODE_ERROR,
                    "respMsg": _("The user should be in the group Inventory"),
                }
            )

            return result.format()

        result.update(
            {
                "respCode": constants.RESPONSE_CODE_OK,
                "assignmentType": 1,
                "operName": self._operator_user.name,
            }
        )

        # Do sign on
        if params.contextType == "1":
            result.update({"contextType": 1, "scenarioStatus": "01"})

            # This query will check if the picker has an open picking.
            # This can happen if the Zetes console crash
            picking_query = """
SELECT picking.id,
  picking_zone.code,
  pick_type.zetes_picking_type
FROM stock_picking AS picking
  LEFT JOIN stock_picking_type AS pick_type
    ON picking.picking_type_id = pick_type.id
  LEFT JOIN picking_zone ON pick_type.picking_zone_id = picking_zone.id
  LEFT JOIN round_instance AS round ON picking.delivery_round_id = round.id
WHERE picking.picking_type_subcode IN ('PICK', 'ARRANGEMENT')
      AND picking.state IN ('partially_available', 'assigned')
      AND picking.zetes_state IN %(picking_zetes_state)s
      AND EXISTS(SELECT 1
                 FROM stock_pack_operation AS operation
                 INNER JOIN stock_location l
                   ON operation.location_id = l.id
                 WHERE operation.picking_id = picking.id
                 AND operation.zetes_state in %(op_zetes_state)s
                 AND l.is_valid_location
                 )
      AND picking.operator_id = %(operator_id)s
ORDER BY round.date, round.time_picking_planned, picking.rank DESC
LIMIT 1;
            """

            query_values = {
                "picking_zetes_state": (constants.AS_START, constants.AS_ACTIVE),
                "operator_id": self._operator_user.id,
                "op_zetes_state": (constants.OP_DEFAULT, constants.OP_SKIPPED),
            }

            self.env.cr.execute(picking_query, query_values)
            query_result = self.env.cr.fetchone()

            # If the user has a assigned picking
            if query_result and query_result[0]:
                result.update(
                    {
                        "unitSlam": 1,
                        "Usf01": query_result[0],
                        "Usf02": query_result[1],
                        "Usf03": query_result[2],
                    }
                )
            else:
                result.unitSlam = 0

        # Do a sign out
        else:
            # Nothing to do for a sign out
            result.contextType = 2

        return result.format()

    def resu(self, params):
        """
        A resu request will never return something.
        When zetes send this type of request, the system doesn't wait
        for a response even if there is an error. We need to catch and manage
        errors by yourself.

        There is no resu resquest for usercontext
        """
        return
