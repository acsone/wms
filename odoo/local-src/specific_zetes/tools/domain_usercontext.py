# -*- coding: utf-8 -*-
from odoo.http import request

from domain_interface import DomainInterface, Parameters


class Usercontext(DomainInterface):
    EXAMPLE_REQU = '208030824,2.2.3,3iV_101,REQU_USERCONTEXT,98,1,20170207,' \
                   '072932,98427733121320,1,,01,,,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030824,2.2.3,3iV_101,RESP_USERCONTEXT,98,1,' \
                   '20170207,072758,98427733121320,0,,1,01,,1,' \
                   'Serge Diplo,,0,,,,,,,,,,'
    EXAMPLE_RESU = '208092662,2.2.3,3iV_101,RESU_USERCONTEXT,87,1,20170207,' \
                   '081534,874277334413394,4,70,,1,Monica Checchi,,,,,,,,,,,,'
    REQU = (
    'contextType', 'requestType', 'scenarioStatus', 'Cri01', 'Cri02', 'Cri03',
    'Cri04', 'Cri05', 'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06',
    'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESP = (
    'respCode', 'respMsg', 'contextType', 'scenarioStatus', 'responseType',
    'assignmentType', 'operName', 'operType', 'unitSlam', 'Usf01', 'Usf02',
    'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')
    RESU = ('contextType', 'scenarioStatus', 'requestType', 'assignmentType',
            'operName', 'operType', 'Usf01', 'Usf02', 'Usf03', 'Usf04',
            'Usf05', 'Usf06', 'Usf07', 'Usf08', 'Usf09', 'Usf10')

    def requ(self, params):
        result = Parameters(self, action='resp')

        user = self._user
        if not user:
            result.update({
                'respCode': 10,
                'respMsg': 'User not found'
            })

            return result.format()

        if not user.has_group('stock.group_stock_user'):
            result.update({
                'respCode': 10,
                'respMsg': 'The user should be in the group Inventory'
            })

            return result.format()

        result.update({
            'respCode': 0,
            'assignmentType': 1,
            'operName': user.name,
        })

        # Do sign on
        if params.contextType == '1':
            result.update({
                'contextType': 1,
                'scenarioStatus': '01',
            })

            picking = request.env['stock.picking'].sudo(self._user).search(
                [('operator_id', '=', self._user.id),
                 ('state', '=', 'assigned'),
                 ('picking_type_code', '=', 'internal')],
                limit=1)

            # If the user has a assigned picking
            if picking:
                result.update({
                    'unitSlam': 1,
                    'Usf01': picking.id,
                })
            else:
                result.unitSlam = 0

        # Do a sign out
        else:
            result.contextType = 2

            pickings = request.env['stock.picking'].sudo(self._user).search([
                ('operator_id', '=', user.id),
                ('state', '=', 'assigned')
            ])
            for picking in pickings:
                bos = request.env['stock.backorder.confirmation'].sudo(self._user) \
                    .create({
                    'picking_id': picking.id,
                })
                for bo in bos:
                    bo.process()

        return result.format()

    def resu(self, params):
        if not self._user:
            return

        pickings = request.env['stock.picking'].sudo(self._user).search([
            ('operator_id', '=', self._user.id),
            ('state', '=', 'assigned')
        ])
        for picking in pickings:
            bo = request.env['stock.backorder.confirmation'].sudo(self._user) \
                .create({'picking_id': picking.id,
                         })
            bo.process()
