# -*- coding: utf-8 -*-
import logging

from openerp.addons.web.http import request

from domain_interface import DomainInterface, Parameters

_logger = logging.getLogger(__name__)


class Refdata(DomainInterface):
    EXAMPLE_REQU = '208030824,2.2.3,3iV_101,REQU_REFDATA,98,1,20170207,' \
                   '072934,98427733121341,,,,,,,,,,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030824,2.2.3,3iV_101,RESP_REFDATA,98,1,20170207,' \
                   '072759,98427733121341,0,,2,01,médicament,,,,,,,,,,,'
    EXAMPLE_RESU = ''
    REQU = (
    'assignmentType', 'scenarioStatus', 'dataTypeList', 'Cri01', 'Cri02',
    'Cri03', 'Cri04', 'Cri05', 'Cri06', 'Cri07', 'Cri08', 'Cri09', 'Cri10',
    'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
    'Usf09', 'Usf10')
    RESP = (
    'respCode', 'respMsg', 'dataType', 'operValue', 'promptInfo', 'hostValue',
    'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
    'Usf09', 'Usf10')
    RESU = ()

    def requ(self, params):
        picking_types = request.env['stock.picking.type'].sudo(self._user).search(
            [('subcode', '=', 'PICK')]
        )
        result = []
        for picking_type in picking_types:
            picking_values = Parameters(self)
            picking_values.update({
                'respCode': 0,
                'dataType': 2,
                'operValue': picking_type.zone_code,
                'promptInfo': picking_type.name
            })
            result.append(picking_values)
        return '\n'.join([line.format() for line in result])

    def resu(self, params):
        print 'Execute method'
