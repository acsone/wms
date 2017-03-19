# -*- coding: utf-8 -*-
from openerp.addons.web.http import request

from domain_interface import DomainInterface, Parameters


class Print(DomainInterface):
    EXAMPLE_REQU = '208030828,2.2.3,3iV_101,REQU_PRINT,30,1,20170207,' \
                   '073426,304277331552660,000000001625844,,,,,' \
                   '03,X,,,,,,,,,,,,,,'
    EXAMPLE_RESP = '208030828,2.2.3,3iV_101,RESP_PRINT,30,1,20170207,' \
                   '073411,304277331552660,0,,000000001625844,,,,,,,,,,' \
                   '17,,,,,,,,,,'
    EXAMPLE_RESU = ''
    REQU = (
    'groupNum', 'groupSubNum', 'headerNum', 'headerSubNum', 'assignmentType',
    'printType', 'printerNum', 'destLocationId', 'destCarSeqNum', 'destCarId',
    'Usf01', 'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
    'Usf09', 'Usf10')
    RESP = ('respCode', 'respMsg', 'groupNum', 'groupSubNum', 'headerNum',
            'headerSubNum', 'printerNum', 'destLocationId', 'destLocationCD',
            'destCarSeqNum', 'destCarId', 'numOfLabels', 'labelCD', 'Usf01',
            'Usf02', 'Usf03', 'Usf04', 'Usf05', 'Usf06', 'Usf07', 'Usf08',
            'Usf09', 'Usf10')
    RESU = ()

    def requ(self, params):
        result = Parameters(self, action='resp')

        picking_id = params.groupNum
        if not picking_id:
            result = Parameters(self, action='resp')
            result.update({
                'respCode': 10,
                'respMsg': 'No picking found with the ID {}'.format(picking_id)
            })
            return result.format()
        picking_id = int(picking_id)

        picking = request.env['stock.picking']\
            .sudo(self._user).browse(picking_id)

        print_type = params.printType
        printer_address = params.printerNum

        result.update({
            'respCode': 0,
        })

        return result.format()

    def resu(self, params):
        print 'Execute method'
