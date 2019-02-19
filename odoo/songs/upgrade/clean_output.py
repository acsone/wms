# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

# wrapping the long lines will make the file unreadable and I cannot spend more
# time refactoring this :(
# ->
# flake8: noqa

import anthem
from odoo import fields


REMOVE = 3
ADD = 4


@anthem.log
def post(ctx):
    """clean output location"""
    fix_packages_shipped_because_of_parent_left_bug(ctx)
    correct_quant_on_wrong_move(ctx)
    fix_shipping_not_recorded(ctx)
    # odoodb_ref2
    kill_waiting_shipments(ctx)


def has_picking_noship_moves(ctx, picking):
    no_ship = (ctx.env.ref('__setup__.deliver_carrier_by_client').id,
               ctx.env.ref('__setup__.deliver_carrier_long_term').id
               )
    return any(m.order_id.carrier_id.id in no_ship for m in picking.move_lines)


def get_picking_stats(picking):
    states = {}
    for move in picking.move_lines:
        states.setdefault(move.state, []).append(move.id)
    states = ['%s: %d' % (state, len(val))
              for (state, val) in states.iteritems()]
    states.sort()
    return "%s\t%s" % (picking.name, ', '.join(states))


def transfer_picking(ctx, picking, date_done=None, change_pick_type=True, force=False):
    fix_pick_type = ctx.env.ref(
        '__setup__.stock_picking_type_fix_ship'
    )
    ctx.log_line(get_picking_stats(picking))
    for pack in picking.pack_operation_ids:
        if pack.product_id:
            pack.qty_done = pack.product_qty
        else:
            pack.qty_done = 1
        for packlot in pack.pack_lot_ids:
            packlot.qty = packlot.qty_todo
        if force:
            if pack.product_id.tracking != 'none':
                packlot_qty = sum(packlot.qty for packlot in pack.pack_lot_ids)
                if packlot_qty < pack.product_qty:
                    unknown_lot = ctx.env['stock.production.lot'].search([('product_id', '=', pack.product_id.id),
                                                                          ('name', '=', 'Unknown')])
                    if not unknown_lot:
                        unknown_lot = ctx.env['stock.production.lot'].create({'product_id': pack.product_id.id,
                                                                              'name': 'Unknown'})
                    pack.write(
                        {'pack_lot_ids': [
                            (0, 0, {'qty': pack.product_qty - packlot_qty,
                                    'lot_id': unknown_lot.id})
                          ]}
                    )
    picking.do_transfer()
    ctx.log_line(get_picking_stats(picking))
    if picking.state == 'done':
        if date_done is None:
            for m in picking.move_lines:
                anc = m.get_ancestors().filtered(lambda r: r.state == 'done')
                if anc:
                    date_done = anc.sorted('date')[-1].date
                    break
        if date_done:
            picking.date_done = date_done
            picking.move_lines.filtered(lambda r: r.state == 'done').write(
                {'date': date_done}
            )
    if picking.state == 'done':
        picking.write({'picking_type_id': fix_pick_type.id})
    if force:
        picking.message_post('Availability was forced on this picking')
    return picking


@anthem.log
def correct_quant_on_wrong_move(ctx):
    """Reattach quant on the correct stock.move"""
    env = ctx.env
    sql = """
    select m.id from stock_move m
    inner join stock_move m2
    on m2.id = m.move_dest_id
    where not exists (select move_id
                      from stock_quant_move_rel
                      where move_id = m.id)
    and m.state = 'done'
    and m2.state not in ('cancel', 'done');
    """
    env.cr.execute(sql)
    move_ids = [r[0] for r in env.cr.fetchall()]
    blocking_moves = env['stock.move'].browse(move_ids)
    # the blocking move is the one which is done but has
    # no stock quant (which has been wrongly assigned to another move)
    for blocking in blocking_moves:
        ctx.log_line('Correcting stock.move %s' % (blocking.id,))
        product = blocking.product_id
        pick = blocking.picking_id
        # find another stock move on the same picking with the same product
        # that have too much quant quantity and move it on the current stock
        # move
        # it is blocking because it prevents the "out" picking (dest) to be
        # available
        for line in pick.move_lines:
            if line == blocking:
                continue
            elif line.product_id != product:
                continue
            quant_sum = sum(line.mapped('quant_ids.qty'))
            if line.product_qty == quant_sum:
                continue
            for quant in line.quant_ids:
                if quant.qty == blocking.product_qty:
                    quant.history_ids = [
                        (REMOVE, line.id),
                        (ADD, blocking.id),
                    ]
                    break
            # now the sum of quants on the line which had too much
            # quants at the beginning should be correct
            quant_sum = sum(line.mapped('quant_ids.qty'))
            assert line.product_qty == quant_sum
            # and the one on the blocking move too
            blocking_quant_sum = sum(blocking.mapped('quant_ids.qty'))
            assert blocking.product_qty == blocking_quant_sum
            if blocking.quant_ids:
                break


def check_stolen_quants(ship_move):
    ancestors = ship_move.get_ancestors().filtered(lambda r: r.state == 'done')
    picked_quants = ancestors.mapped('quant_ids')
    shipped_quants = ship_move.mapped('quant_ids')
    picked_not_shipped = picked_quants - shipped_quants
    return picked_not_shipped


def get_last_move(quant):
    return quant.history_ids.filtered(lambda rec: rec.location_dest_id == quant.location_id)


def find_quant_to_swap(ship_move, needed_qty, seen=None):
    seen = set() if seen is None else seen
    #output_loc = ctx.env['stock.location'].browse(16)
    #fix_output_20191220 = ctx.env['stock.location'].browse(14327)
    result = ship_move.env['stock.quant']
#    import pdb; pdb.set_trace()
    quants = check_stolen_quants(ship_move)
    in_output = quants.filtered(lambda r: r.location_id.id in (16, 14327))
    for q in in_output:
        if needed_qty < q.qty:
            q._quant_split(needed_qty)
        result |= q
        needed_qty -= q.qty
        if needed_qty <= 0:
            break
    if needed_qty > 0:
        others = quants - in_output
        if others:
            for other in others:
                if other.id in seen:
                    continue
                seen.add(other.id)
                last_move = get_last_move(other)
                result |= find_quant_to_swap(last_move, needed_qty, seen)
    return result


@anthem.log
def correct_stolen_ships(ctx):
    """fix quants shipped by SHIP pickings for which they were not meant"""
    # called by fix_shipping_not_recorded
    output_loc = ctx.env['stock.location'].browse(16)
    fix_output_20191220 = ctx.env['stock.location'].browse(14327)
    assert fix_output_20191220.name == 'Fix Sortie 20181220'
    waiting_moves = ctx.env['stock.move'].search(
        [('location_id', '=', output_loc.id),
         ('state', '=', 'waiting')]
    )
    pickup_delivery = ctx.env.ref('__setup__.deliver_carrier_by_client')
    long_term_delivery = ctx.env.ref('__setup__.deliver_carrier_long_term')

    no_back_moves = ctx.env['stock.move'].search(
        [('location_id', '=', output_loc.id),
         ('state', '=', 'cancel'),
         ('picking_id.state', '=', 'done'),
         ('picking_id.partner_id.is_sale_back_order_accepted', '=', False),
         ]
    ).filtered(
        lambda rec:
            rec.order_id.carrier_id not in (pickup_delivery,
                                            long_term_delivery)
    )
    waiting_moves |= no_back_moves
    move_ids = []
    for move in waiting_moves:
        anc = move.get_ancestors()
        if anc.mapped('state') != ['done']:
            continue
        elif anc.mapped('quant_ids.location_id') != move.location_id:
            move_ids.append(move.id)
        # else:
        #     move.picking_id.to_process_quant_expired = True
    blocked_moves = ctx.env['stock.move'].browse(move_ids)
    for move in blocked_moves:
        ancestors = move.get_ancestors().filtered(lambda r: r.state == 'done')
        for anc in ancestors:
            quants = anc.mapped('quant_ids').filtered(
                lambda r: r.location_id != output_loc
            )
            for quant in quants:
                if quant.location_id == move.location_id:
                    quant.write({'reservation_id': move.id})
                elif quant.location_id == fix_output_20191220:
                    # case 1: the quant we want to deliver was stolen by the
                    # Fix Sortie operation
                    # -> move it out, and reserve it.
                    quant.write({'location_id': 16,
                                 'reservation_id': move.id})
                elif quant.location_id.name == 'Customers':
                    last_move = quant.history_ids.filtered(
                        lambda r: r.location_dest_id == quant.location_id
                    )[0]
                    last_move_pick = last_move.get_ancestors()
                    last_move_pick_quants_in_output = \
                        last_move_pick.quant_ids.filtered(
                            lambda rec:
                                rec.location_id.id in (output_loc.id,
                                                       fix_output_20191220.id)
                        )
                    if move.split_from == last_move:
                        # normal case: the SHIP was split
                        continue
                    elif last_move_pick_quants_in_output:
                        # case 2: our quant was stolen and delivered to someone
                        # else.
                        # -> Find quant that was picked to satisfy the SHIP which
                        # stole the quant, and make it so that this quant is
                        # flagged as shipped. Then put back our quant in place, and
                        # reserve it.
                        last_move.write(
                            {'quant_ids': [
                                # swap!
                                (ADD, q.id, 0) for q in last_move_pick_quants_in_output] +
                             [
                                (REMOVE, quant.id, 0),
                             ]
                             }
                        )
                        # XXX check if both quants have the same lot, if not, we
                        # need to reprint the SHIP
                        last_move_pick_quants_in_output.write(
                            {'location_id': quant.location_id.id}
                        )
                        quant.write({'location_id': 16,
                                     'reservation_id': move.id})
                    elif last_move_pick.product_qty > sum(last_move_pick.mapped('quant_ids.qty')):
                        # Case 3: odoo bug with mixed up split of quants when
                        # multiple lines with same product: the quant is still in
                        # output, but it is linked to the wrong PICK move and
                        # therefore cannot be reserved on our SHIP move
                        # -> fix the association of the quants in the PICK moves
                        pick_pick = last_move_pick.picking_id
                        other_pick_moves = pick_pick.move_lines.filtered(
                            lambda rec: rec.id != last_move_pick.id and rec.product_id == last_move_pick.product_id and rec.move_dest_id.state == 'done'
                        )
                        free_quants = other_pick_moves.mapped('quant_ids') - other_pick_moves.mapped('move_dest_id.quant_ids')
                        if sum(free_quants.mapped('qty')) == last_move_pick.product_qty - sum(last_move_pick.mapped('quant_ids.qty')):
                            for m in other_pick_moves:
                                (m.quant_ids & free_quants).write(
                                    {'history_ids': [(REMOVE, m.id, 0),
                                                     (ADD, last_move_pick.id, 0),
                                                     ],
                                     'reservation_id': move.id,
                                     }
                                )
                        else:
                            continue
                            raise Exception('unhandled case')
                    elif last_move.product_qty < sum(
                            last_move.mapped('quant_ids.qty')):
                        # Case 4: for some unknown reason, the output move who
                        # stole our quant just shipped more qty than requested
                        # (WTF!)  I checked, this has no impact on the sale
                        # order line.
                        # -> get back our quant and reserve it
                        last_move.write({'quant_ids': [(REMOVE, quant.id, 0)]})
                        quant.write({'location_id': 16,
                                     'reservation_id': move.id})
                    elif move in quant.history_ids:
                        # Case 5 : for some unknown reason, the quant is in
                        # Customers but the move is not done (because it cannot
                        # be reserved, of course...)
                        quant.write({'location_id': 16,
                                     'reservation_id': move.id,
                                     'history_ids': [(REMOVE, move.id, 0)]})
                    elif not last_move_pick:
                        # Case 6: the move was stolen in an extra move
                        # these are not reported in sales
                        # -> put back the quant in output (XXX)
                        quant.write(
                            {'location_id': 16,
                             'reservation_id': move.id,
                             'history_ids': [(REMOVE, last_move.id, 0)]}
                        )
                        # XXX delete last_move?
                    elif all(
                            q.location_id.name == 'Customers' for q in last_move_pick.quant_ids
                            ):
                        # Case 7: like case 2, but the substitution happened
                        # more than once.
                        quants_to_swap = find_quant_to_swap(last_move, quant.qty)
                        last_move.write(
                            {'quant_ids': [
                                # swap!
                                (ADD, q.id, 0) for q in quants_to_swap
                                ] + [
                                (REMOVE, quant.id, 0),
                             ]
                             }
                        )
                        quants_to_swap.write(
                            {'location_id': quant.location_id.id}
                        )
                        quant.write({'location_id': 16,
                                     'reservation_id': move.id})
                    else:
                        ctx.log_line(
                            "\t".join(str(v)
                                      for v in (move.id,
                                                quant.id,
                                                move.product_id.display_name,
                                                move.picking_id.name,
                                                anc.picking_id.name,
                                                quant.location_id.name,
                                                last_move.id,
                                                last_move_pick))
                        )
                        continue
                        raise Exception('unhandled case')
                if sum(
                        move.mapped('reserved_quant_ids.qty')
                       ) == move.product_qty:
                    # everything is ok, no need to consider other quants in the
                    # PICK
                    break
    # allow next method to catch them
    blocked_moves.write({'reservation_id': False})
    return blocked_moves


@anthem.log
def fix_packages_shipped_because_of_parent_left_bug(ctx):
    """fix the pickings affected by package creation race condition

    the parent_left column was renamed parent_left_bak in the 10.30.18
    migration before the nested set implementation was dropped on the
    stock.quant.package model.

    TODO: remove the backup columns

    """
    Pack = ctx.env['stock.quant.package']
    fix_pick_type = ctx.env.ref(
        '__setup__.stock_picking_type_fix_ship'
    )
    # find all package that were hit by the race condition
    duplicate_parent_left_query = (
        "SELECT id FROM stock_quant_package "
        "WHERE parent_left_bak IN "
        "    (SELECT parent_left_bak "
        "     FROM stock_quant_package "
        "     GROUP BY parent_left_bak "
        "     HAVING COUNT(id) > 1 "
        "     )"
    )
    ctx.env.cr.execute(duplicate_parent_left_query)
    ids = [pleft for (pleft,) in ctx.env.cr.fetchall()]
    ids.sort()
    # For each package, check if it was shipped as being a subpackage
    # of another package to an unintended customer.
    # When this happens, the stock.move in the package are labelled as "extra
    # moves" and the pack is not listed in teh pack moved by the picking's pack
    # operations
    EXTRA_MOVE_PREFIX = (u'Extra Move', u'Mouvement suppl\xe9mentaire')
    for pack in Pack.browse(ids):
        pack_moves = pack.mapped('quant_ids.history_ids').filtered(
            lambda rec: rec.name.startswith(EXTRA_MOVE_PREFIX)
        )
        wrong_moves = pack_moves.filtered(
            lambda rec: rec.picking_id.pack_operation_pack_ids
        )
        if not wrong_moves:
            # all is good, next pack!
            continue
        # something fishy was found, get the PICK which created the package
        undue_products = [(q.qty, q.product_id.name) for q in pack.quant_ids]
        wrong_shipping = wrong_moves.mapped('picking_id')
        pick_moves = pack.mapped('quant_ids.history_ids').filtered(
            lambda rec: rec.location_dest_id.id == 16  # output location
        )
        expected_moves = pick_moves.mapped('move_dest_id')
        # XXX do we need this context?
        expected_ship = expected_moves.mapped('picking_id').with_context(
            skip_pdf_gen=1,
        )
        if wrong_shipping.name == expected_ship.name:
            # both packs affected by the problem were shipped in the same
            # picking -> let it be.
            continue
        # To fix the mess:
        # * change the picking type of the picking and of the picking
        #   which thought it did not ship the good
        # * log an explanation on the chatter
        # * make sure the additional moves don't have procurement_id
        # * remove the stock.moves which were not shipped with this picking
        # * flag the dest moves as shipped
        wrong_shipping.write({'picking_type_id': fix_pick_type.id})
        wrong_shipping.message_post(
            'Delivery correction: '
            'removing %s wrongly counted in the shipped quantities.\n\n'
            'Please print again the delivery slip.' %
            u','.join(['%s %s' % prod for prod in undue_products]),
            content_subtype="text"
        )
        to_delete = []
        for move in wrong_shipping.move_lines:
            if (move.name.startswith(EXTRA_MOVE_PREFIX) and
                    move.product_id in pack.mapped('quant_ids.product_id')):
                if ((move.procurement_id
                        and move.procurement_id.product_id != move.product_id) or
                        # this one is a special case where the same product was
                        # ordered twice with the same product and picked
                        # simultaneously
                        move.id == 617018):
                    order_line = move.order_line_id
                    move.procurement_id = False
                    order_line.qty_delivered = order_line._get_delivered_qty()
                to_delete.append(move.id)
        ctx.env.cr.execute(
            'DELETE FROM stock_move WHERE id in %s', (tuple(to_delete),)
        )
        pack.quant_ids.write({'location_id': 16})   # move back in Sortie
        expected_ship.action_assign()
        transfer_picking(ctx, expected_ship,
                         date_done=wrong_shipping.date_done)
        expected_ship.message_post(
            'Delivery correction: '
            ' the following products were shipped on %s:\n'
            '%s\n'
            'Please print the delivery slip and send to the customer.\n\n'
            'Check the invoicing of %s' %
            (wrong_shipping.date_done,
             u'\n'.join(['%s %s' % prod for prod in undue_products]),
             u', '.join(expected_moves.mapped('order_id.name')),
             ),
            content_subtype="text"
        )


@anthem.log
def fix_shipping_not_recorded(ctx):
    """flag as shipped the shippings which were missed

    the pickings are placed in a special picking type to be processed
    we process the following cases:

    * picking was done, and the picked quant is still in Output and the
      delivery method is not "enlevé par client" or "long terme", ship move
      pending

    * picking was done, and the picked quant is still in Output, ship move
      canceled, ship picking done (no backorder policy)

    """
    fix_pick_type = ctx.env.ref(
        '__setup__.stock_picking_type_fix_ship'
    )
    pickup_delivery = ctx.env.ref('__setup__.deliver_carrier_by_client')
    long_term_delivery = ctx.env.ref('__setup__.deliver_carrier_long_term')
    quants = ctx.env['stock.quant'].search(
        [('location_id', '=', 16),
         ('qty', '>', 0),
         # ('reservation_id', '=', False),
         ],
        order='id'
    )
    quants.mapped('reservation_id.picking_id').do_unreserve()
    no_backorder_picking_ids = set()
    waiting_picking_ids = set()
    skipped_picking_ids = set()
    picking_pick_date = {}
    blocked_picking_ids = set()
    for quant in quants:
        moves = quant.history_ids.filtered(
            lambda r: r.location_dest_id.id == 16
        ).sorted('date')
        if not moves:
            continue
        # last time the quant reached Output
        move = moves[-1]
        dest = find_ship_move(move)
        order = dest.order_id
        if not dest or not order:
            continue
        if order.carrier_id in (pickup_delivery, long_term_delivery):
            # ctx.log_line("Skipping %s (%s)" % (dest.picking_id.name,
            #                                    order.carrier_id.name))
            # Some SHIPs contain a mix of moves related to different
            # carriers. We choose to skip them altogether for now
            skipped_picking_ids.add(dest.picking_id.id)
            continue
        if dest.state == 'cancel' and dest.picking_id.state == 'done':
            # no backorder policy
            no_backorder_picking_ids.add(dest.picking_id.id)
            dest.write({'state': 'waiting'})
            dest.action_assign()
        elif dest.state not in ('done', 'cancel'):
            waiting_picking_ids.add(dest.picking_id.id)
            picking_pick_date[dest.picking_id] = move.picking_id.date_done
    to_fix_pickings = ctx.env['stock.picking'].browse(
        list((no_backorder_picking_ids | waiting_picking_ids) -
             skipped_picking_ids)
    )
    to_fix_pickings.do_unreserve()
    blocked_moves = correct_stolen_ships(ctx)
    blocked_pickings = blocked_moves.mapped('picking_id')
    to_fix_pickings = (to_fix_pickings | blocked_pickings).sorted(
        'create_date'
    )
    # XXX do we need this context?
    count = 0
    ctx.log_line('Checking availability')
    # needed in case some moves have pack
    to_fix_pickings.mapped(
        'move_lines').filtered(
            lambda rec: rec.state not in ('cancel', 'done')
        ).mapped('linked_move_operation_ids').unlink()
    memorize_quant_expired = {}
    for pick in to_fix_pickings:
        memorize_quant_expired[pick.id] = pick.to_process_quant_expired
    to_fix_pickings.write({'to_process_quant_expired': True})
    with ctx.log('action_assign on %d pickings' % len(to_fix_pickings)):
        to_fix_pickings.action_assign()
    for picking in to_fix_pickings.with_context(skip_pdf_gen=1):
        count += 1
        ctx.log_line('* %02d/%02d %s' %
                     (count, len(to_fix_pickings), picking.name))
        if picking.id in no_backorder_picking_ids:
            assigned_moves = picking.move_lines.filtered(
                lambda rec: rec.state == 'assigned')
            if not assigned_moves:
                continue
            affected_sales = assigned_moves.mapped('order_id')
            undue_products = [(move.product_uom_qty, move.product_id.name)
                              for move in assigned_moves]
            date_done = picking.date_done
            picking = transfer_picking(ctx, picking, date_done)
            ctx.log_line("-> %s" % picking.state)
        else:
            assigned_moves = picking.move_lines.filtered(
                lambda rec: rec.state == 'assigned')
            if picking.state not in ('assigned', 'partially_available'):
                continue

            # XXX we use the date_done of one latest the PICK. Maybe wrong, but
            # otherwise we would need to split the SHIP...
            pick_pickings = ctx.env['stock.move'].search(
                [('move_dest_id', 'in', picking.move_lines.ids),
                 ('state', '=', 'done')]
            ).mapped('picking_id').sorted('date_done')
            if pick_pickings:
                date_done = pick_pickings[-1].date_done
            else:
                date_done = fields.Datetime.now()

            picking = transfer_picking(ctx, picking, date_done)
            ctx.log_line("-> %s" % picking.state)
            if picking.state != 'done':
                continue
            affected_sales = picking.move_lines.mapped('order_id')
            undue_products = [(move.product_uom_qty, move.product_id.name)
                              for move in assigned_moves]
        picking.write(
            {'to_process_quant_expired': memorize_quant_expired[picking.id],
             }
        )
        picking.message_post(
            'Delivery correction: '
            ' the following products were shipped on %s:\n'
            '%s\n'
            'Please print the delivery slip and send to the customer.\n\n'
            'Check the invoicing of %s' %
            (date_done,
             u'\n'.join(['%s %s' % prod for prod in undue_products]),
             u', '.join(affected_sales.mapped('name')),
             ),
            content_subtype="text"
        )


def find_ship_move(pick_move):
    """does the oposite of move.get_ancestors()"""
    Move = pick_move  # for search
    ship_move = pick_move.move_dest_id
    if ship_move:
        while True:
            backorder = Move.search(
                [('split_from', '=', ship_move.id)])
            if backorder:
                ship_move = backorder
            else:
                break
    return ship_move


@anthem.log
def check_quants_in_output(ctx):
    """Fix the quants in output

    we look at the PICK move which moved the quant and the chained SHIPS
    * some are attached to a ship move which is done -> change the
      quant location

    * some are attached to a ship move which is assigned -> ship
    * some are attached to a ship move which is waiting: do nothing

    """
    no_ship = (ctx.env.ref('__setup__.deliver_carrier_by_client'),
               ctx.env.ref('__setup__.deliver_carrier_long_term')
               )
    quants = ctx.env['stock.quant'].search(
        [('location_id', '=', 16), ('qty', '>', 0)]
    )
    pick_ids = {}
    leftover_quants = []
    dont_touch_quants = []
    for q in quants:
        pick = q.history_ids.filtered(
            lambda r: r.location_dest_id == q.location_id).sorted('date')
        if pick:
            pick = pick[-1]
        ship = find_ship_move(pick)
        order = ship.order_id
        if not ship:
            leftover_quants.append(q.id)
        elif order.carrier_id in no_ship:
            dont_touch_quants.append(q.id)
        else:
            leftover_quants.append(q.id)
    dont_touch_quants = ctx.env['stock.quant'].browse(dont_touch_quants)
    leftover_quants = ctx.env['stock.quant'].browse(leftover_quants)
    # move the leftover quants out of packages
    leftover_quants.write({'package_id': False})
    return dont_touch_quants, leftover_quants


@anthem.log
def kill_waiting_shipments(ctx):
    """Force Ship waiting shipments that have been picked"""
    pickup_delivery = ctx.env.ref('__setup__.deliver_carrier_by_client')
    long_term_delivery = ctx.env.ref('__setup__.deliver_carrier_long_term')
    ships = ctx.env['stock.move'].search(
        [('location_id', '=', 16), ('state', '=', 'waiting')],
        order='picking_id'
    )
    to_force = []
    assigned = []
    todo_states = set(['confirmed', 'assigned', 'waiting'])
    dont_touch_quants, available_quants = check_quants_in_output(ctx)
    nb_ships = len(ships)
    counter = 0
    for ship in ships:
        counter += 1
        if counter % 500 == 0:
            ctx.log_line('Examining ship move %d/%d' % (counter, nb_ships))
        if ship.reserved_quant_ids:
            print ship.reserved_quant_ids
        ship.action_assign()
        if ship.state == 'assigned':
            if has_picking_noship_moves(ctx, ship.picking_id):
                continue
            else:
                assigned.append(ship.id)
            continue
        # ship is waiting
        pick = ship.get_ancestors().sorted('date')
        if len(pick) == 0:
            ctx.log_line("no pick for %s" % ship)
            """no pick for stock.move(297754,)
            no pick for stock.move(298643,)
            no pick for stock.move(315840,)
            no pick for stock.move(317179,)
            """
            ship.action_cancel()
            ship.picking_id.message_post(
                'Cancelled shipment of %s (qty=%s) because '
                'procurement chain is broken (no picking move found)'
                'Please manually change the sale order.' %
                (ship.product_id.display_name, ship.product_qty)
            )
            ship.picking_type_id = ctx.env.ref('__setup__.stock_picking_type_fix_ship')
            continue
        else:
            pick = pick[-1]

        if pick.mapped('state') == ['done']:
            ctx.log_line(
                'forcing %s: pick is in state %s' % (ship, pick.state)
            )
            to_force.append(ship.id)
        elif todo_states & set(pick.mapped('state')):
            continue
        else:
            ctx.log_line(
                u'skipping %s: pick %s is in state %s' %
                (ship, pick.mapped('picking_id.name'), pick.mapped('state'))
            )
    to_force = ctx.env['stock.move'].browse(to_force)
    to_force.force_assign()
    assigned = ctx.env['stock.move'].browse(assigned)
    pickings = (to_force | assigned).mapped('picking_id')
    for picking in pickings:
        transfer_picking(ctx, picking, force=True)
        picking.message_post('This delivery was forced pushed. The lot numbers are probably incorrect.')
    for quant in available_quants:
        # clean output of leftover quants
        if quant.location_id.id == 16:
            move = ctx.env['stock.move'].create(
                {'location_id': 16,
                 'location_dest_id': 5,  # inventory loss
                 'name': 'correction inventaire 20190210: %s' % quant.product_id.display_name,
                 'product_id': quant.product_id.id,
                 'product_uom': quant.product_id.uom_id.id,
                 'product_uom_qty': quant.qty,
                })
            quant.reservation_id = move
            move.action_done()

@anthem.log
def restore_quants_in_fix_sortie(ctx):
    """Move back the required quants from Fix Sortie 20181220"""
    output_loc = ctx.env['stock.location'].browse(16)
    fix_output_20191220 = ctx.env['stock.location'].browse(14327)
    assert fix_output_20191220.name == 'Fix Sortie 20181220'
    quants = ctx.env['stock.quant'].search(
        [('location_id', '=', fix_output_20191220.id),
         ('qty', '>', 0)]
    )
    ship_ids = []
    for q in quants:
        pick = q.history_ids.filtered(
            lambda r: r.location_dest_id == output_loc).sorted('date')
        if pick:
            pick = pick[-1]
        ship = find_ship_move(pick)
        order = ship.order_id
        if ship.state not in ('done', 'cancel'):
            q.write({'location_id': output_loc.id,
                     'reservation_id': ship.id,
                     })
            ship_ids.append(ship.id)
    moves = ctx.env['stock.move'].browse(ship_ids)
    with ctx.log('assigning %d moves' % len(moves)):
        # question: is it required? or must it be avoided?
        moves.action_assign()
        for move in moves:
            move.picking_id.message_post(
                '<p>Restored the picked quants for %s that had been '
                'stored away in december 2018, and flagged the '
                'move as available<p>''' % (move.product_id.display_name,))

    for pick in moves.mapped('picking_id').sorted('id'):
        ctx.log_line('%s: %s' % (pick.name, pick.state))
