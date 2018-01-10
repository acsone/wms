# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, post_install, at_install


class TestPickingBackorder(TransactionCase):

    def setUp(self):
        super(TestPickingBackorder, self).setUp()
        self.product_model = self.env['product.product']
        self.partner_model = self.env['res.partner']
        self.location_model = self.env['stock.location']
        self.stock_picking_model = self.env['stock.picking']
        self.backorder_reason_model = self.env['stock.backorder.reason']
        self.backorder_choice_model = self.env['stock.backorder.choice']
        self.backorder_confirmation_model = (
            self.env['stock.backorder.confirmation']
        )
        self.helpdesk_ticket_model = self.env['helpdesk.ticket']
        self.helpdesk_ticket_reason_model = self.env['helpdesk.ticket.reason']

        self.product = self.product_model.create({
            'name': 'Unittest P1',
            'uom_id': self.ref('product.product_uom_unit'),
            'type': 'product',
        })

        self.partner = self.partner_model.create({
            'name': 'Unittest supplier',
            'is_sale_back_order_accepted': False,
        })

        self.supplier_location = self.location_model.browse(
            self.ref('stock.stock_location_suppliers')
        )
        self.customer_location = self.location_model.browse(
            self.ref('stock.stock_location_customers')
        )
        self.stock_location = self.location_model.browse(
            self.ref('stock.stock_location_stock')
        )
        self.output_location = self.location_model.browse(
            self.ref('stock.stock_location_output')
        )
        self.grn = self.env['stock.grn'].create({
            'carrier_id': self.partner.id,
            })

    @post_install(True)
    @at_install(False)
    def test_1_purchase_picking_backorder_create_backorder_no_helpdesk(self):
        # Define helpdesk ticket values
        ticket_reason = self.helpdesk_ticket_reason_model.create({
            'name': 'Unittest helpdesk ticket reason',
        })
        ticket_default_name = 'Ticket default name'

        def test():
            # Define the backorder behavior on partner
            self.partner.is_purchase_back_order_accepted = (
                backorder_accepted
            )

            # Define backorder reason
            backorder_reason = self.backorder_reason_model.create({
                'name': 'Unittest backorder',
                'backorder_action_to_do': backorder_action,
                'is_helpdesk_ticket_to_create': helpdesk_needed,
                'helpdesk_ticket_reason_id': ticket_reason.id,
                'helpdesk_ticket_default_name': ticket_default_name,
            })

            # Create picking
            picking = self.stock_picking_model.create({
                'picking_type_id': picking_type_id,
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'partner_id': self.partner.id,
                'move_lines': [
                    (0, 0, {
                        'name': 'a move',
                        'product_id': self.product.id,
                        'product_uom_qty': 10,
                        'product_uom': self.product.uom_id.id,
                        'location_id': self.supplier_location.id,
                        'location_dest_id': self.stock_location.id,
                    })
                ],
                'grn_id': self.grn.id,
            })

            # Transfer picking partially
            picking.action_confirm()
            picking.force_assign()
            self.assertEqual(len(picking.pack_operation_product_ids), 1)
            pack_operation = picking.pack_operation_product_ids
            pack_operation.write({
                'qty_done': 3,
            })
            result = picking.do_new_transfer()

            # Check that the transfer action return the good wizard
            self.assertEqual(
                result['res_model'],
                'stock.backorder.choice'
            )

            # Create backorder choice wizard and execute it
            wizard = self.backorder_choice_model.with_context(
                result['context']
            ).create({
                'reason_id': backorder_reason.id,
            })
            wizard.onchange_type()
            wizard.apply()

            # Search created backorder
            backorder = self.stock_picking_model.search([
                ('backorder_id', '=', picking.id)
            ])

            # Check picking values
            self.assertEqual(len(picking.move_lines), 1)
            self.assertEqual(picking.move_lines.product_id, self.product)
            self.assertEqual(picking.move_lines.product_uom_qty, 3)
            self.assertEqual(picking.move_lines.state, 'done')
            self.assertEqual(picking.state, 'done')

            # Check backorder values
            self.assertEqual(len(backorder), 1)
            self.assertEqual(backorder.move_lines.product_uom_qty, 7)
            keep_backorder = (
                backorder_action == 'create' or
                (
                    backorder_action == 'use_partner_option' and
                    backorder_accepted
                )
            )
            self.assertEqual(
                backorder.state,
                'confirmed' if keep_backorder else 'cancel'
            )

            # Check helpdesk ticket creation
            ticket = self.helpdesk_ticket_model.search([
                ('ref', '=', 'stock.picking,%s' % picking.id),
            ])
            if helpdesk_needed:
                self.assertEqual(len(ticket), 1)
                self.assertEqual(ticket.partner_id, self.partner)
                self.assertEqual(
                    ticket.helpdesk_ticket_reason_id,
                    ticket_reason
                )
                self.assertEqual(ticket.name, ticket_default_name)
            else:
                self.assertEqual(len(ticket), 0)

        # Test all cases
        purchase_case = (
            self.ref('stock.picking_type_in'),
            self.customer_location.id,
            self.stock_location.id,
        )
        customer_return_case = (
            self.ref('stock.picking_type_in'),
            self.customer_location.id,
            self.stock_location.id,
        )
        for backorder_action in ['create', 'cancel', 'use_partner_option']:
            for backorder_accepted in [False, True]:
                for helpdesk_needed in [False, True]:
                    for picking_type_id, location_id, location_dest_id in [
                        purchase_case, customer_return_case
                    ]:
                        test()

    @post_install(True)
    @at_install(False)
    def test_2_sale_and_other_picking_backorder(self):
        """
        We take like sale case
        This case use the standard Odoo feature.
        """

        # Test all cases
        sale_case_1 = (
            self.ref('stock.picking_type_out'),
            self.stock_location.id,
            self.customer_location.id
        )
        sale_case_2 = (
            self.ref('stock.picking_type_out'),
            self.stock_location.id,
            self.output_location.id
        )
        for sale_backorder_accepted in [False, True]:
            for purchase_backorder_accepted in [False, True]:
                for create_backorder in [False, True]:
                    for picking_type_id, location_id, location_dest_id in [
                        sale_case_1, sale_case_2
                    ]:
                        # Define the backorder behavior on partner
                        self.partner.write({
                            'is_sale_back_order_accepted':
                                sale_backorder_accepted,
                            'is_purchase_back_order_accepted':
                                purchase_backorder_accepted,
                        })

                        # Create picking
                        picking = self.stock_picking_model.create({
                            'picking_type_id': picking_type_id,
                            'location_id': location_id,
                            'location_dest_id': location_dest_id,
                            'partner_id': self.partner.id,
                            'move_lines': [
                                (0, 0, {
                                    'name': 'a move',
                                    'product_id': self.product.id,
                                    'product_uom_qty': 10,
                                    'product_uom': self.product.uom_id.id,
                                    'location_id': location_id,
                                    'location_dest_id': location_dest_id,
                                })
                            ],
                            'grn_id': self.grn.id,
                        })

                        # Transfer picking partially
                        picking.action_confirm()
                        picking.force_assign()
                        pack_operation = picking.pack_operation_product_ids
                        pack_operation.write({
                            'qty_done': 3,
                        })
                        result = picking.do_new_transfer()

                        # Check that the transfer action return the good wizard
                        self.assertEqual(
                            result['res_model'],
                            'stock.backorder.confirmation'
                        )

                        # Create backorder confirmation wizard and execute it
                        wizard = self.backorder_confirmation_model.create({
                            'pick_id': picking.id
                        })
                        if create_backorder:
                            wizard.process()
                        else:
                            wizard.process_cancel_backorder()

                        # Search created backorder
                        backorder = self.stock_picking_model.search([
                            ('backorder_id', '=', picking.id)
                        ])

                        # Check picking values
                        self.assertEqual(
                            picking.pack_operation_product_ids.product_qty, 3
                        )
                        self.assertEqual(picking.state, 'done')

                        # Check backorder values
                        self.assertEqual(len(backorder), 1)
                        self.assertEqual(
                            backorder.move_lines.product_uom_qty, 7
                        )
                        self.assertEqual(
                            backorder.state,
                            'confirmed' if create_backorder else 'cancel'
                        )
