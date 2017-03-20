# -*- coding: utf-8 -*-
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
    'assignmentType', 'requestType', 'tripCounter', 'Cri01', 'Cri02', 'Cri03',
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
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'assignmentStatus',
    'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
    'Usf09', 'Usf10')

    def requ(self, params):
        result = Parameters(self, action='resp')

        if not params.Cri02:
            domain = [
                ('state', '=', 'assigned'),
                ('picking_type_code', '=', 'internal'),
                '|',
                ('zetes_state', '=', False),
                ('zetes_state', '=', '05'),
            ]

            zone_code = params.Cri01
            if zone_code:
                zone = request.env['stock.picking.type'].sudo(self._user).search([
                    ('zone_code', '=', zone_code)
                ])
                domain.append(('picking_type_id', '=', zone.id))

            if params.requestType:
                domain.append(('operator_id', '=', False))
            else:
                domain.append(('operator_id', '=', self._user.id))

            picking = \
                request.env['stock.picking'].sudo(self._user).search(domain, limit=1)

        else:
            picking_id = int(params.Cri02)
            picking = request.env['stock.picking'].sudo(self._user).browse(picking_id)

        if not len(picking):
            result.update({
                'respCode': 10,
                'respMsg': 'Cannot found a picking'
            })
            return result.format()

        # Assign a new checksum for this picking
        picking.sudo(self._user).assign_picking_checksum()

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
            'assignmentStatus': '00',
            'Usf02': partner.alcyon_category_id.name,
            'Usf03': round,
            'Usf04': 0,
            'Usf05': 0,
            'Usf06': 'C', # TODO see future password field on partner
            'Usf07': partner.name,
            'Usf08': '{} {}'.format(partner.zip, partner.city), # Zip + city
            'Usf09': len(picking.pack_operation_product_ids), # Nbr of operation
            'Usf10': None,
        })

        return result.format()

    def resu(self, params):
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
            })
        elif params.assignmentStatus in ['04', '08']:
            result = picking.sudo(self._user).do_new_transfer()

            if isinstance(result, dict):
                model = result.get('res_model')
                wizard = \
                    request.env[model].sudo(self._user)\
                        .browse(int(result.get('res_id')))

                wizard.process()
        elif params.assignmentStatus == '05':
            picking.sudo(self._user).cancel_picking()
