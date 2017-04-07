# -*- coding: utf-8 -*-
from odoo import _
from odoo.http import request

from domain_interface import DomainInterface, Parameters


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
        result = Parameters(self, action='resp')

        if not params.Cri02:
            query_values = []
            picking_query = """
SELECT picking.id
FROM stock_picking AS picking
  LEFT JOIN stock_picking_type AS type ON picking.picking_type_id = type.id
WHERE picking.state = 'assigned'
      AND type.code = 'internal'
      AND picking.zetes_state IN ('00', '05')
      AND EXISTS(SELECT 1
                 FROM stock_pack_operation AS operation
                 WHERE operation.picking_id = picking.id
                 AND operation.zetes_state IN ('00', '03'))
            """

            zone_code = params.Cri01
            if zone_code:
                zone = \
                    request.env['stock.picking.type'].sudo(self._user).search([
                        ('zone_code', '=', zone_code)
                    ])
                picking_query += "AND picking.picking_type_id = %s "
                query_values.append(zone.id)

            if params.requestType:
                picking_query += "AND picking.operator_id IS NULL "
            else:
                picking_query += "AND picking.operator_id = %s"
                query_values.append(self._user.id)

            picking_query += "ORDER BY id LIMIT 1;"
            request.env.cr.execute(picking_query, tuple(query_values))
            query_result = request.env.cr.fetchone()

            if query_result and query_result[0]:
                picking_id = query_result[0]
                picking = \
                    request.env['stock.picking'] \
                        .sudo(self._user).browse(picking_id)
            else:
                picking = []

        else:
            picking_id = int(params.Cri02)
            picking = \
                request.env['stock.picking'] \
                    .sudo(self._user).browse(picking_id)

        if not len(picking):
            result.update({
                'respCode': 10,
                'respMsg': _('Cannot found a picking')
            })
            return result.format()

        partner = picking.partner_id

        # TODO FIX the sudo
        round = None
        if picking.sudo().delivery_round_id \
                and picking.sudo().delivery_round_id.vehicle_id:
            round = picking.sudo().delivery_round_id.vehicle_id.name[:2]

        result.update({
            'respCode': 0,
            'assignmentType': 1,
            'groupNum': picking.id,
            'Usf02': partner.alcyon_category_id.name,
            'Usf03': round,
            'Usf04': 0,
            'Usf05': 0,
            'Usf07': partner.name,
            'Usf08': '{} {}'.format(partner.zip, partner.city),  # Zip + city
            'Usf09': len(picking.pack_operation_product_ids),
            # Nbr of operation
            'Usf10': None,
        })

        if partner.is_passport_required:
            result.Usf06 = 'C'  # This partner request a double control
        else:
            result.Usf06 = 'E'  # Simple packaging

        if picking.zetes_state == '05':
            result.update({
                'assignmentStatus': '01',
                'Usf01': picking.checksum,
            })
        else:
            result.assignmentStatus = '00'

        return result.format()

    def resu(self, params):
        """
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

        picking = request.env['stock.picking'].browse(int(picking_id))
        if not len(picking_id):
            return

        picking.sudo(self._user).zetes_state = params.assignmentStatus
        # The picking is done
        if params.assignmentStatus in ['01', '02']:
            picking.sudo(self._user).write({
                'operator_id': self._user.id,
                'state': 'in_progress',
                'printed': True,
            })
        elif params.assignmentStatus in ['04', '08']:
            # If the picking required a verification (passport)
            # the number of label is 0. The number of label cannot be 0
            # for a standard picking (without passport).
            if not params.Usf01:
                picking.sudo(self._user).write({
                    'state': 'check_required'
                })
            else:
                result = picking.sudo(self._user).do_new_transfer()

                if isinstance(result, dict):
                    model = result.get('res_model')
                    wizard = \
                        request.env[model].sudo(self._user) \
                            .browse(int(result.get('res_id')))

                    wizard.process()
        elif params.assignmentStatus == '05':
            picking.sudo(self._user).interrupt_picking()
