# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def activate_options(ctx):
    """ Activating logistics options """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids': [(4, ctx.env.ref('stock.group_production_lot').id),
                        (4, ctx.env.ref('stock.group_locations').id),
                        (4, ctx.env.ref('stock.group_adv_location').id)]

    })


@anthem.log
def set_delivery_pick_ship(ctx):
    """ Setting pick-ship on the warehouse """
    ctx.env.ref('stock.warehouse0').delivery_steps = 'pick_ship'


@anthem.log
def create_locations(ctx):
    """ Creating stock locations """
    loc_stock = ctx.env.ref('stock.stock_location_stock')

    locations = [
        ('__init.stock_location_materiel', u'Matériel'),
        ('__init.stock_location_ali', u'Aliments'),
        ('__init.stock_location_medoc', u'Médicaments'),
        ('__init.stock_location_froid', u'Froid'),
        # ('__init.stock_location_congel', u'Congel -12'),
    ]

    for xmlid, name in locations:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': loc_stock.id,
            'subcode': 'PICK',
        })

    sub_locations = [
        ('__init.stock_location_frigo', u'Frigo',
         ctx.env.ref('__init.stock_location_froid').id),
        ('__init.stock_location_parking_medoc', u'Parking Medicaments',
         ctx.env.ref('stock.stock_location_company').id),
    ]

    for xmlid, name, location_id in sub_locations:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': location_id,
            'subcode': 'PICK',
        })


@anthem.log
def create_putaway(ctx):
    """ Create putaway and putaway strat
    """
    ref = ctx.env.ref

    loc_stock_id = ref('stock.stock_location_stock').id

    create_or_update(ctx, 'product.putaway', '__init.stock_putaway_parking', {
        'name': u'Parking',
        'method': u'fixed',
        'fixed_location_id': loc_stock_id,
    })

    create_or_update(
        ctx, 'stock.fixed.putaway.strat', '__init.stock_putaway_parking_medoc',
        {
            'putaway_id': ref('__init.stock_putaway_parking').id,
            'category_id': ref('__init.product_categ_medoc').id,
            'fixed_location_id': ref('__init.stock_location_parking_medoc').id,
        }
    )

    create_or_update(ctx, 'stock.location', 'stock.stock_location_company', {
        'location_id': loc_stock_id,
        'putaway_strategy_id': ref('__init.stock_putaway_parking').id
    })

    create_or_update(ctx, 'stock.picking.type', 'stock.picking_type_in', {
        'default_location_dest_id': ref('stock.stock_location_company').id
    })


@anthem.log
def create_picking_types(ctx):
    """ Creating picking types """
    picking_sequence = ctx.env['ir.sequence'].search(
        [('name', '=', 'Alcyon Belux SA Sequence picking')],
        limit=1,
    )

    internal_sequence = ctx.env['ir.sequence'].search(
        [('name', '=', 'Alcyon Belux SA Sequence internal')],
        limit=1,
    )

    location_stock = ctx.env.ref('stock.stock_location_stock')
    location_out = ctx.env.ref('stock.stock_location_output')
    location_mat = ctx.env.ref('__init.stock_location_materiel')
    location_ali = ctx.env.ref('__init.stock_location_ali')
    location_medoc = ctx.env.ref('__init.stock_location_medoc')
    location_froid = ctx.env.ref('__init.stock_location_froid')
    location_parking_medoc = ctx.env.ref('__init.stock_location_parking_medoc')
    types = [
        {'xmlid': '__init.stock_picking_type_materiel',
         'name': 'Pick Matériel',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_mat.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         },
        {'xmlid': '__init.stock_picking_type_ali',
         'name': 'Pick Aliments',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_ali.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         },
        {'xmlid': '__init.stock_picking_type_medoc',
         'name': 'Pick Médicaments',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         # 'default_location_src_id': location_medoc.id,
         'default_location_src_id': location_stock.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         },
        {'xmlid': '__init.stock_picking_type_froid',
         'name': 'Pick Frigo',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_froid.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         },
        {'xmlid': '__init.stock_picking_type_rangement',
         'name': 'Rangement Medicaments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_medoc.id,
         'default_location_dest_id': location_medoc.id,
         'use_create_lots': False,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'stock.picking.type', xmlid, record)


@anthem.log
def create_procurement_rules(ctx):
    """ Creating procurement rules """
    ref = ctx.env.ref
    location_out = ref('stock.stock_location_output')
    warehouse = ctx.env.ref('stock.warehouse0')
    types = [
        {'xmlid': '__init.procurement_rule_materiel',
         'sequence': 15,
         'name': 'WH: Stock -> Output (MAT)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__init.stock_location_materiel').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__init.stock_picking_type_materiel').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__init.procurement_rule_ali',
         'sequence': 15,
         'name': 'WH: Stock -> Output (ALI)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__init.stock_location_ali').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__init.stock_picking_type_ali').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__init.procurement_rule_medoc',
         'sequence': 15,
         'name': 'WH: Stock -> Output (MED)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         # 'location_src_id': ref('__init.stock_location_medoc').id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__init.stock_picking_type_medoc').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__init.procurement_rule_froid',
         'sequence': 15,
         'name': 'WH: Stock -> Output (FRIGO)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__init.stock_location_froid').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__init.stock_picking_type_froid').id,
         'group_propagation_option': 'propagate',
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'procurement.rule', xmlid, record)


@anthem.log
def create_routes(ctx):
    """ Creating routes """
    ref = ctx.env.ref
    types = [
        {'xmlid': '__init.stock_location_route_pick_materiel',
         'name': 'Alcyon Belux SA: Pick (MAT)',
         'pull_ids': [(6, 0, ref('__init.procurement_rule_materiel').ids)],
         },
        {'xmlid': '__init.stock_location_route_pick_ali',
         'name': 'Alcyon Belux SA: Pick (ALI)',
         'pull_ids': [(6, 0, ref('__init.procurement_rule_ali').ids)],
         },
        {'xmlid': '__init.stock_location_route_pick_medoc',
         'name': 'Alcyon Belux SA: Pick (MED)',
         'pull_ids': [(6, 0, ref('__init.procurement_rule_medoc').ids)],
         },
        {'xmlid': '__init.stock_location_route_pick_froid',
         'name': 'Alcyon Belux SA: Pick (FROID)',
         'pull_ids': [(6, 0, ref('__init.procurement_rule_froid').ids)],
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        record.update({
         'sequence': 20,
         'product_categ_selectable': True,
         'product_selectable': False,
        })
        create_or_update(ctx, 'stock.location.route', xmlid, record)


@anthem.log
def assign_route_categories(ctx):
    """ Assigning routes to product categories """
    ref = ctx.env.ref
    categs = [('__init.product_categ_materiel',
               '__init.stock_location_route_pick_materiel'),
              ('__init.product_categ_ali',
               '__init.stock_location_route_pick_ali'),
              ('__init.product_categ_medoc',
               '__init.stock_location_route_pick_medoc'),
              ('__init.product_categ_frigo',
               '__init.stock_location_route_pick_froid'),
              ]
    for category_xmlid, route_xmlid in categs:
        ref(category_xmlid).route_ids = [(6, 0, ref(route_xmlid).ids)]


@anthem.log
def main(ctx):
    """ Configuring logistics """
    activate_options(ctx)
    set_delivery_pick_ship(ctx)
    create_locations(ctx)
    create_putaway(ctx)
    create_picking_types(ctx)
    create_procurement_rules(ctx)
    create_routes(ctx)
    assign_route_categories(ctx)
