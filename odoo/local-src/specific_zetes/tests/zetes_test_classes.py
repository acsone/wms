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

        self.env.user.write({
            'tz': 'Europe/Brussels'
        })

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
            'is_sale_back_order_accepted': True,
        })

        round_template = self.env['round.template'].create({
            'code': ROUND_CODE,
            'name': 'Test',
            'time_leave_planned': 12.50,
            'time_picking_planned': 12.50,
        })

        round_itinerary = self.env['round.itinerary'].create({
            'sequence': 100,
            'name': 'Test itinerary',
            'template_ids': [(6, 0, [round_template.id])],
            'partner_position_ids': [(0, 0, {
                'sequence': 1,
                'partner_id': self.partner.id,
            })]
        })

        self.round = self.env['round.instance'].create({
            'name': 'TOUR/20170101/01',
            'template_id': round_template.id,
            'date': fields.Date.today(),
            'time_leave_planned': 12.50,
            'time_picking_planned': 12.50,
            'itinerary_ids': [(6, 0, [round_itinerary.id])],
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
            'type': 'product',
        })

        location_obj = self.env['stock.location']

        self.parent_location = location_obj.create({
            'name': 'G',
            'location_id': self.env.ref('stock.stock_location_stock').id
        })

        self.location_product_1 = location_obj.create({
            'name': 'GD01B1',
            'kind': 'bin',
            'zone': 'G',
            'corridor': 'D',
            'shelf': '01',
            'height': 'B',
            'box': '1',
            'location_id': self.parent_location.id,
            'bin_checksum_1': '123',
            'bin_checksum_2': '123',
        })
        self.env['stock.location']._parent_store_compute()

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

        self.product_1.write({
            'stock_bin_ids': [(0, 0, {
                'sequence': 1,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'bin_location_id': self.location_product_1.id,
            })]
        })

        self.picking_zone_medoc = self.env.ref(
            '__setup__.picking_zone_medicament', raise_if_not_found=False)
        if not self.picking_zone_medoc:
            self.picking_zone_medoc = self.env['picking.zone'].create({
                'code': '01',
                'name': 'Medicament',
            })

        # The picking type "Medoc" is create after test
        # However I test if the database already contains this picking type
        self.picking_type_medoc = \
            self.env.ref('__setup__.stock_picking_type_medoc',
                         raise_if_not_found=False)
        if not self.picking_type_medoc:
            wh = self.env.ref('stock.warehouse0')
            picking_sequence = wh.pick_type_id.sequence_id
            location_stock = self.env.ref('stock.stock_location_stock')
            location_out = self.env.ref('stock.stock_location_output')
            self.picking_type_medoc = self.env['stock.picking.type'].create({
                'name': 'Pick Médicaments',
                'code': 'internal',
                'sequence_id': picking_sequence.id,
                'default_location_src_id': location_stock.id,
                'default_location_dest_id': location_out.id,
                'use_create_lots': False,
                'subcode': 'PICK',
                'groupbypartner': True,
                'color': 7,
                'sequence': 4,
                'picking_zone_id': self.picking_zone_medoc.id,
            })

        tomorrow = datetime.now() + relativedelta(days=1)
        self.picking = self.env['stock.picking'].create({
            'partner_id': self.partner.id,
            'picking_type_id': self.picking_type_medoc.id,
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
            # Round to the picking
            self.round.button_update()

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


class ZetesParkingTest(ZetesTest):
    def setUp(self):
        super(ZetesParkingTest, self).setUp()

        # Create a parking Medoc
        self.parking_medoc = self.env['stock.location'].create({
            'name': 'Parking Medoc',
            'kind': 'parking',
            'usage': 'internal',
            'location_id': self.env.ref('stock.stock_location_company').id,
            'picking_zone_id': self.picking_zone_medoc.id,
        })
        self.env['stock.location']._parent_store_compute()

        # Set a quantity in this parking
        update_qty_wizard = self.env['stock.change.product.qty'].create({
            'product_id': self.product_1.id,
            'product_tmpl_id': self.product_1.product_tmpl_id.id,
            'new_quantity': 100,
            'location_id': self.parking_medoc.id
        })
        update_qty_wizard.change_product_qty()

        self.picking_type_medoc = self.env.ref(
            '__setup__.stock_picking_type_rangement_medoc',
            raise_if_not_found=False)
        if not self.picking_type_medoc:
            wh = self.env.ref('stock.warehouse0')
            internal_sequence = wh.int_type_id.sequence_id
            location_medoc = self.env.ref('__setup__.stock_location_medoc')
            self.picking_type_medoc = self.env['stock.picking.type'].create({
                'name': 'Rangement Medicaments',
                'code': 'internal',
                'sequence_id': internal_sequence.id,
                'default_location_src_id': self.parking_medoc.id,
                'default_location_dest_id': location_medoc.id,
                'use_create_lots': False,
                'sequence': 9,
                'picking_zone_id': self.picking_zone_medoc.id,
            })
        self.parking_medoc.write({
            'barcode_picking_type_id': self.picking_type_medoc.id,
        })
