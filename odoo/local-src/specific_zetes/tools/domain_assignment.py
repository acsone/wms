# -*- coding: utf-8 -*-
from datetime import date
import logging

from odoo import _

from domain_interface import DomainInterface, Parameters
from .. import constants

_logger = logging.getLogger(__name__)


class Assignment(DomainInterface):
    EXAMPLE_REQU = '208030828,2.2.3,3iV_101,REQU_ASSIGNMENT,30,1,20170207,' \
                   '072835,30427733115352,1,1,1,01,,,,,,,,,,,,,,,,,,,,,,,,,' \
                   ',,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030828,2.2.3,3iV_101,RESP_ASSIGNMENT,30,1,20170207,' \
                   '072820,30427733115352,0,,1,1,000000001625844,,00,,' \
                   'Vétérinaires,95,0,0,C,CLINIQUE VET. DU MONT-FALISE,' \
                   '4520 WANZE,00018,'
    EXAMPLE_RESU = '208030828,2.2.3,3iV_101,RESU_ASSIGNMENT,30,1,20170207,' \
                   '072836,30427733115363,000000001625844,,,,' \
                   '01,123456789,,,,,,,,,,'
    REQU = (
        'assignmentType', 'requestType', 'tripCounter', 'Cri01', 'Cri02',
        'Cri03',
        'Cri04', 'Cri05', 'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10', 'Cri11',
        'Cri12', 'Cri13', 'Cri14', 'Cri15', 'Cri16', 'Cri17', 'Cri18', 'Cri19',
        'Cri20', 'Cri21', 'Cri22', 'Cri23', 'Cri24', 'Cri25', 'Cri26', 'Cri27',
        'Cri28', 'Cri29', 'Cri30', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05',
        'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESP = (
        'respCode', 'respMsg', 'assignmentType', 'responseType', 'groupNum',
        'groupSubNum', 'assignmentStatus', 'Usf01', 'Usf02', 'Usf03', 'Usf04',
        'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESU = (
        'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum',
        'assignmentStatus',
        'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
        'Usf09', 'Usf10')

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
        result = Parameters(self, action='resp')

        assignment_type = params.assignmentType and int(params.assignmentType)
        # Search for a standard picking
        if assignment_type == constants.PICKING_ASSIGNMENT:
            picking = self.get_picking(params)
            result.assignmentType = constants.PICKING_ASSIGNMENT
        # Search for a picking assignment
        elif assignment_type == constants.PARKING_ASSIGNMENT:
            picking = self.get_picking_parking(params)
            result.assignmentType = constants.PARKING_ASSIGNMENT
        # Search for a picking in reserve
        elif assignment_type == constants.RESERVE_ASSIGNMENT:
            picking = self.get_picking_reserve(params)
            result.assignmentType = constants.RESERVE_ASSIGNMENT
        else:
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('Unknown assignment type')
            })
            return result.format()

        if not picking:
            result.update({
                'respCode': constants.RESPONSE_CODE_ERROR,
                'respMsg': _('Cannot found a picking')
            })
            return result.format()

        # There are two bin checksum on location
        # According the day of the month, the picking have to use the "Right"
        # or "Left" checkum. For the even day, the picking take the checksum
        # on the right (=> bin_checksum_1) and for the odoo day, the picker
        # take the checksum on the left (=> bin_checksum_2)
        is_odd_day = date.today().day % 2
        if is_odd_day:
            result.Usf07 = _('Left')
        else:
            result.Usf07 = _('Right')

        partner = picking.partner_id

        round_name = picking.sudo().delivery_round_id.template_id.code

        result.update({
            'respCode': constants.RESPONSE_CODE_OK,
            'groupNum': picking.id,
            'Usf02': partner.alcyon_category_id.name,
            'Usf03': round_name,
            'Usf04': 0,  # Constant value
            'Usf05': 0,  # Constant value
            'Usf08': '{} {}'.format(partner.zip, partner.city),  # Zip + city
            'Usf09': len(picking.pack_operation_product_ids),
            # Nbr of operation
            'Usf10': None,
        })

        if partner.is_passport_required:
            result.Usf06 = 'C'  # This partner request a double control
        else:
            result.Usf06 = 'E'  # Simple packaging

        if picking.zetes_state == constants.AS_CANCELED:
            result.update({
                'assignmentStatus': constants.AS_START,
                'Usf01': picking.checksum,
            })
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

        picking = self.request.env['stock.picking'].browse(int(picking_id))
        if not len(picking):
            return

        try:
            picking.sudo(self._user).zetes_state = params.assignmentStatus
            # The picking is done
            if params.assignmentStatus in [constants.AS_START,
                                           constants.AS_ACTIVE]:
                picking.sudo(self._user).assign_operator()
            elif params.assignmentStatus in [constants.AS_DONE,
                                             constants.AS_FINISHED]:
                # If the picking required a verification (passport)
                # the number of label is 0. The number of label cannot be 0
                # for a standard picking (without passport).
                if params.Usf01:
                    # The method "do_new_transfer" is the method called when
                    # an user click on "Validate" on a picking.
                    result = picking.sudo(self._user).do_new_transfer()

                    # In Odoo this button will open a wizard in following case:
                    # 1. A wizard if no quantity has been defined on lines
                    #   (this wizard will set the quantity on each lines)
                    # 2. A wizard if we need to create a back order
                    if isinstance(result, dict):
                        model = result.get('res_model')
                        wizard = self.request.env[model].sudo(self._user)\
                            .browse(int(result.get('res_id')))

                        # Fortunately these wizards have the same
                        # method "process" to execute the wizard
                        wizard.process()
            elif params.assignmentStatus == constants.AS_CANCELED:
                picking.sudo(self._user).interrupt_picking()
        except Exception as e:
            _logger.error(str(e))
            params.log(picking_id=picking_id, exception=e)

    def get_picking(self, params):
        """
        Return a picking
        :param params:
        :return:
        """
        # If the picker request a new picking (Cri02 is the picking ID)
        if not params.Cri02:
            picking_query = """
            SELECT picking.id
            FROM stock_picking AS picking
              INNER JOIN stock_picking_type AS type
                ON picking.picking_type_id = type.id
              LEFT JOIN picking_zone ON type.picking_zone_id = picking_zone.id
              INNER JOIN round_instance AS round
                ON picking.delivery_round_id = round.id
            WHERE picking.delivery_round_state = 'open'
                  AND type.subcode = 'PICK'
                  AND picking.zetes_state IN %s
                  AND picking.zetes_picking_type = %s
                  AND EXISTS(SELECT 1
                             FROM stock_pack_operation AS operation
                             WHERE operation.picking_id = picking.id
                             AND operation.zetes_state in %s)
                    """
            query_values = [
                (constants.AS_DEFAULT, constants.AS_CANCELED),
                constants.PICKING_ASSIGNMENT,
                (constants.OP_DEFAULT, constants.OP_SKIPPED),
            ]

            # Search a picking in a specific zone (like Food)
            zone_code = params.Cri01
            if zone_code:
                picking_query += "AND picking_zone.code = %s "
                query_values.append(zone_code)

            # If requestType is completed we looking
            # for a picking without an operator
            if params.requestType:
                picking_query += "AND picking.operator_id IS NULL "
            else:
                picking_query += "AND picking.operator_id = %s"
                query_values.append(self._user.id)

            picking_query += "ORDER BY round.date, " \
                             "round.time_picking_planned, " \
                             "picking.rank DESC " \
                             "LIMIT 1;"
            self.request.env.cr.execute(picking_query, tuple(query_values))
            query_result = self.request.env.cr.fetchone()

            if query_result and query_result[0]:
                picking_id = query_result[0]
                picking = self.request.env['stock.picking'] \
                    .sudo(self._user).browse(picking_id)
            else:
                return False
        # If the picker want to continue a picking (Cri02 is not empty)
        else:
            picking_id = int(params.Cri02)
            picking = self.request.env['stock.picking'] \
                .sudo(self._user).browse(picking_id)

        return picking

    def get_picking_parking(self, params):
        """
        Return parking
        :param params:
        :return:
        """

        picking_query = """
        SELECT picking.id
        FROM stock_picking AS picking
          INNER JOIN stock_picking_type AS type
            ON picking.picking_type_id = type.id
          INNER JOIN round_instance AS round
            ON picking.delivery_round_id = round.id
        WHERE picking.zetes_state IN %s
          AND picking.zetes_picking_type = %s
          AND EXISTS(SELECT 1
                     FROM stock_pack_operation AS operation
                     WHERE operation.picking_id = picking.id
                     AND operation.zetes_state IN %s)
                """
        query_values = [
            (constants.AS_DEFAULT, constants.AS_CANCELED),
            constants.PARKING_ASSIGNMENT,
            (constants.OP_DEFAULT, constants.OP_SKIPPED),
        ]

        # Search a picking in a specific zone (like Food)
        zone_code = params.Cri01
        if zone_code:
            zone = \
                self.request.env['stock.picking.type'].sudo(self._user) \
                    .search([('zone_code', '=', zone_code)])
            picking_query += "AND picking.picking_type_id = %s "
            query_values.append(zone.id)

        # If requestType is completed we looking
        # for a picking without an operator
        if params.requestType:
            picking_query += "AND picking.operator_id IS NULL "
        else:
            picking_query += "AND picking.operator_id = %s"
            query_values.append(self._user.id)

        picking_query += "ORDER BY picking.rank DESC " \
                         "LIMIT 1;"

        self.request.env.cr.execute(picking_query, tuple(query_values))
        query_result = self.request.env.cr.fetchone()

        if query_result and query_result[0]:
            picking_id = query_result[0]
            picking = self.request.env['stock.picking'] \
                .sudo(self._user).browse(picking_id)
            return picking

        # Picking not found. Try to create a new one.
        domain = [('reservation_id', '=', False),
                  ('location_id', 'child_of', 'Parking')]
        zone_code = params.Cri01
        if zone_code:
            # TODO Manage Zone Code
            pass

        model_name = 'report.stock.quant.bylocation'
        report = self.request.sudo(self._user).env[model_name].search(
            domain,
            limit=1,
            order='refill_priority'
        )

        if not report:
            return False

        # Create the picking
        picking = report.sudo(self._user).create_picking()
        picking.button_fillwithstock()
        return picking

    def get_picking_reserve(self, params):
        """
        Return reserve
        :param params:
        :return:
        """
        picking_query = """
                SELECT picking.id
                FROM stock_picking AS picking
                  INNER JOIN stock_picking_type AS type
                    ON picking.picking_type_id = type.id
                  INNER JOIN round_instance AS round
                    ON picking.delivery_round_id = round.id
                WHERE picking.zetes_state IN %s
                  AND picking.zetes_picking_type = %s
                  AND EXISTS(SELECT 1
                             FROM stock_pack_operation AS operation
                             WHERE operation.picking_id = picking.id
                             AND operation.zetes_state IN %s)
                        """
        query_values = [
            (constants.AS_DEFAULT, constants.AS_CANCELED),
            constants.RESERVE_ASSIGNMENT,
            (constants.OP_DEFAULT, constants.OP_SKIPPED),
        ]

        # Search a picking in a specific zone (like Food)
        zone_code = params.Cri01
        if zone_code:
            zone = \
                self.request.env['stock.picking.type'].sudo(self._user) \
                    .search([('zone_code', '=', zone_code)])
            picking_query += "AND picking.picking_type_id = %s "
            query_values.append(zone.id)

        # If requestType is completed we looking
        # for a picking without an operator
        if params.requestType:
            picking_query += "AND picking.operator_id IS NULL "
        else:
            picking_query += "AND picking.operator_id = %s"
            query_values.append(self._user.id)

        picking_query += "ORDER BY picking.rank DESC " \
                         "LIMIT 1;"

        self.request.env.cr.execute(picking_query, tuple(query_values))
        query_result = self.request.env.cr.fetchone()

        if query_result and query_result[0]:
            picking_id = query_result[0]
            picking = self.request.env['stock.picking'] \
                .sudo(self._user).browse(picking_id)
            return picking

        # Picking not found. Try to create a new one.
        domain = []
        zone_code = params.Cri01
        if zone_code:
            # TODO Manage Zone Code
            pass

        model_name = 'report.stock.quant.bylocation.reserve'
        report = self.request.sudo(self._user).env[model_name].search(
            domain,
            limit=1,
            order='refill_priority'
        )

        if not report:
            return False

        # Create the picking
        picking = report.sudo(self._user).create_picking()
        picking.button_fillwithstock()
        return picking
