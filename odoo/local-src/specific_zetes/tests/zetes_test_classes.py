# -*- coding: utf-8 -*-
import importlib
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase

from .. import constants
from ..tools.domain_interface import Parameters

DOMAIN = 'http://localhost:8069/zetes/'
OPERATOR_CODE = '99'
DEFAULT_HEADER = ['208030824', '2.2.3', '3iV_101', 'REQU_USERCONTEXT',
                  OPERATOR_CODE, '1', '20170207', '072932', '98427733121320']
ROUND_CODE = 99
PARTNER_NAME = 'Mr. Docteur Test'


class ZetesTest(TransactionCase):
    post_install = True
    at_install = False

    def setUp(self):
        super(ZetesTest, self).setUp()

        # Set all picking as finished (to not interfere with tests)
        query = "UPDATE stock_picking SET zetes_state = %s"
        self.env.cr.execute(query, (constants.AS_FINISHED, ))

        existing_user = self.env['res.users'].search(
            [('operator_code', '=', OPERATOR_CODE)]
        )
        if existing_user:
            raise Exception('An user already exist with the operator code %s.'
                            ' We cannot execute tests without an user '
                            'from scratch.' % OPERATOR_CODE)

        self.user = self.env['res.users'].create({
            'name': 'User test',
            'login': 'zetes_user_test',
            'operator_code': OPERATOR_CODE,
            'groups_id': [(4, self.env.ref('stock.group_stock_user').id)],
            'tz': 'Europe/Brussels',
            'lang': 'en_US',
            'email': 'hello@world.com',
        })

        self.partner = self.env['res.partner'].create({
            'name': PARTNER_NAME,
            'is_back_order_accepted': True,
        })

        round_template = self.env['round.template'].create({
            'code': ROUND_CODE,
            'name': 'Test',
            'time_leave_planned': 12.50,
            'time_picking_planned': 12.50,
        })

        self.round = self.env['round.instance'].create({
            'name': 'TOUR/20170101/01',
            'template_id': round_template.id,
            'date': fields.Date.today(),
            'time_leave_planned': 12.50,
            'time_picking_planned': 12.50,
        })
        self.round.button_confirm()

        # Product 1
        # Location: GAA210
        self.product_1 = self.env['product.product'].create({
            'name': 'Test medoc 1',
            'default_code': '1234567',
            'categ_id': self.env.ref('specific_data.product_categ_medoc').id,
            'tracking': 'lot',
            'list_price': 100,
        })

        self.location_product_1 = self.env.ref('__import__.location_loc_GAA210')
        self.location_product_1.write({
            'bin_checksum_1': '123',
            'bin_checksum_2': '123',
        })

        one_year = datetime.now() + relativedelta(years=1)
        self.lot_product_1 = self.env['stock.production.lot'].create({
            'name': '000000001',
            'product_id': self.product_1.id,
            'life_date': fields.Datetime.to_string(one_year),
        })
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_1.id,
            'product_tmpl_id': self.product_1.product_tmpl_id.id,
            'new_quantity': 100,
            'lot_id': self.lot_product_1.id,
            'location_id': self.location_product_1.id
        })
        update_qty_wizard.change_product_qty()

        tomorrow = datetime.now() + relativedelta(days=1)
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id':
                self.env.ref('__setup__.stock_picking_type_medoc').id,
            'delivery_round_id': self.round.id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_output').id,
            'min_date': fields.Datetime.to_string(tomorrow),
            'zetes_state': constants.AS_DEFAULT,
            'move_lines': [(0, 0, {
                'name': 'Test medoc 1',
                'product_id': self.product_1.id,
                'product_uom_qty': 10,
                'product_uom': self.env.ref('product.product_uom_unit').id,
            })]
        })

        if not hasattr(self, 'disable_picking_validation'):
            self.picking.action_assign()

        self.context = {}

    def format_result(self, result):
        """
        Convert a result (a string) to a Parameters object.
        This object will be use to handle values
        :param result:
        :return:
        """
        # Convert the string to a list
        result_formatted = result.split(',')

        # Remove first empty value (all result starts with a comma)
        result_formatted.pop(0)

        # Extract response values
        result_values = result_formatted[len(DEFAULT_HEADER):]

        # Retrieve the method (eg: RESP_USERCONTEXT)
        method = result_formatted[constants.METHOD_INDEX]
        action, domain = method.split('_')

        # Create an instance of the domain (eg: usercontext = > Usercontext)
        module_name = \
            'openerp.addons.specific_zetes.tools.domain_{}'.format(
                domain.lower())
        module_obj = importlib.import_module(module_name)
        instance = getattr(module_obj, domain.title())(DEFAULT_HEADER,
                                                       request_overwrite=self)

        # Create the instance of Parameter with the previous domain instance
        result_parameter = Parameters(instance,
                                      action=action,
                                      values=result_values)

        return result_parameter
