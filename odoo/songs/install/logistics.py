# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from anthem.lyrics.records import create_or_update


@anthem.log
def company_settings(ctx):
    company = ctx.env.ref('base.main_company')
    company.write({
        'delivery_terms_conditions':
            "<p>Pour être livré le jour de livraison prévu, veuillez passer "
            "vos commandes :<br/>"
            "<b>Par Internet</b> <u>www.alcyonbelux.be</u> : "
            "avant <b>9h15</b> le jour de livraison.<br/>"
            "<b>Par fax ou répondeur</b>: avant <b>9h00</b> "
            "le jour de livraison.<br/>"
            "<b>Par téléphone</b> (sauf pour les médicaments): "
            "avant <b>9h00</b> le jour de livraison</p>"
            "<p>Seules seront prises en considération les demandes de "
            "retours signalées dans les 48 heures de la réception "
            "de la marchandise.<br/>"
            "Elles devront être faites aurpès de notre "
            "<b>service Qualité</b> au <b>04/338.84.22</b> "
            "ou pas email <b>qualite@alcyonbelux.be</b> "
            "ou par fax <b>04/338.84.35</b>.</p>"
    })


@anthem.log
def activate_options(ctx):
    """ Activating logistics options """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids':
            [(4, ctx.env.ref('stock.group_production_lot').id),
             (4, ctx.env.ref('stock.group_stock_multi_locations').id),
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
    root = ctx.env.ref('stock.stock_location_locations')

    # Input
    create_or_update(ctx, 'stock.location', 'stock.stock_location_company', {
        'usage': 'view',
        'active': True,
    })

    # Reserves = Products available => under WH, above Stock
    reserves = [
        ('__setup__.stock_location_reserve_ali', 'Réserve Aliments',
         loc_stock.location_id.id),
        ('__setup__.stock_location_reserve_medoc', 'Réserve Médicaments',
         loc_stock.location_id.id),
    ]
    for xmlid, name, location_id in reserves:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': location_id,
            'usage': 'view',
            'kind': 'reserve',
        })

    # Bins = Products available to pick => under Stock
    locations = [
        ('__setup__.stock_location_materiel', 'Matériel',
         False,
         loc_stock.id),
        ('__setup__.stock_location_ali', 'Aliments',
         ctx.env.ref('__setup__.stock_location_reserve_ali').id,
         loc_stock.id),
        ('__setup__.stock_location_medoc', 'Médicaments',
         ctx.env.ref('__setup__.stock_location_reserve_medoc').id,
         loc_stock.id),
        ('__setup__.stock_location_froid', 'Froid',
         False,
         loc_stock.id),
    ]
    for xmlid, name, reserve_id, location_id in locations:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': location_id,
            'reserve_location_id': reserve_id,
            'usage': 'view',
        })
    locations = [
        ('__setup__.stock_location_frigo', 'Frigo',
         False,
         ctx.env.ref('__setup__.stock_location_froid').id),
    ]
    for xmlid, name, reserve_id, location_id in locations:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': location_id,
            'reserve_location_id': reserve_id,
            'usage': 'view',
        })

    # Parking is under Input (part of stock)
    parkings = [
        (
            '__setup__.stock_location_parking_medoc',
            'Parking Medicaments',
            'view'
        ),
        (
            '__setup__.stock_location_parking_ali',
            'Parking Aliments',
            'internal'
        ),
        (
            '__setup__.stock_location_parking_materiel',
            'Parking Matériel',
            'internal'
        ),
        (
            '__setup__.stock_location_parking_frigo',
            'Parking Frigo',
            'internal'
        ),
    ]
    for xmlid, name, usage in parkings:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': ctx.env.ref('stock.stock_location_company').id,
            'usage': usage,
            'kind': 'parking',
        })

    # Achetés-Vendus is under Input (part of stock)
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_onorder',
        {
            'name': 'Achetés-Vendus',
            'location_id': ctx.env.ref('stock.stock_location_company').id,
            'usage': 'view',
        })
    onorders = [
        ('__setup__.stock_location_order_ali', 'Achetés-Vendus Aliments'),
        ('__setup__.stock_location_order_medoc',
         'Achetés-Vendus Médicaments'),
        ('__setup__.stock_location_order_frigo', 'Achetés-Vendus Frigo'),
        ('__setup__.stock_location_order_mat', 'Achetés-Vendus Matériel'),
    ]
    for xmlid, name in onorders:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': ctx.env.ref('__setup__.stock_location_onorder').id,
            'usage': 'internal',
        })

    # Returns = Products unavailable => not under WH but under physical loc.
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_return',
        {
            'name': 'Retours',
            'location_id': root.id,
            'usage': 'view',
        })
    returns = [
        ('__setup__.stock_location_return_ali', 'Retours Aliments'),
        ('__setup__.stock_location_return_medoc', 'Retours Médicaments'),
        ('__setup__.stock_location_return_frigo', 'Retours Frigo'),
        ('__setup__.stock_location_return_mat', 'Retours Matériel'),
        ]
    for xmlid, name in returns:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': ctx.env.ref('__setup__.stock_location_return').id,
            'usage': 'internal',
        })

    # Casse = Products unavailable => not under WH but under physical locations
    loc_partner = ctx.env.ref('stock.stock_location_locations_partner')
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_destroyed', {
            'name': 'Détruit',
            'location_id': loc_partner.id,
            'usage': 'customer',
        })
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_destroy',
        {
            'name': 'Casse',
            'location_id': root.id,
            'usage': 'view',
        })
    destroy = [
        ('__setup__.stock_location_destroy_all', 'A détruire'),
        ]
    for xmlid, name in destroy:
        create_or_update(ctx, 'stock.location', xmlid, {
            'name': name,
            'location_id': ctx.env.ref('__setup__.stock_location_destroy').id,
            'usage': 'internal',
        })

    # Pharma
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_pharma',
        {
            'name': 'Pharma',
            'location_id': loc_partner.id,
            'usage': 'customer',
        })


@anthem.log
def create_putaway(ctx):
    """ Create putaway and putaway strat
    """
    ref = ctx.env.ref

    loc_stock_id = ref('stock.stock_location_stock').id

    # Input - Manage Parking and Achetés-vendus
    create_or_update(ctx, 'product.putaway', '__setup__.stock_putaway_input', {
        'name': 'Input',
        'method': 'fixed',
        'fixed_location_id': loc_stock_id,
    })
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_onorder',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('stock.route_warehouse0_mto').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_onorder').id,
        }
    )

    parking_strat = [
        ('__setup__.stock_putaway_strat_parking_medoc',
         'specific_data.product_categ_medoc',
         '__setup__.stock_location_parking_medoc'),
        ('__setup__.stock_putaway_strat_parking_aliment',
         'specific_data.product_categ_ali',
         '__setup__.stock_location_parking_ali'),
        ('__setup__.stock_putaway_strat_parking_materiel',
         'specific_data.product_categ_materiel',
         '__setup__.stock_location_parking_medoc'),
        ('__setup__.stock_putaway_strat_parking_materiel',
         'specific_data.product_categ_frigo',
         '__setup__.stock_location_parking_frigo'),
        ]
    for xmlid, categ, loc in parking_strat:
        create_or_update(
            ctx, 'stock.fixed.putaway.strat', xmlid,
            {
                'putaway_id': ref('__setup__.stock_putaway_input').id,
                'category_id': ref(categ).id,
                'fixed_location_id': ref(loc).id,
            }
        )
    create_or_update(ctx, 'stock.location', 'stock.stock_location_company', {
        'location_id': loc_stock_id,
        'putaway_strategy_id': ref('__setup__.stock_putaway_input').id
    })

    # Input - Manage Achetés-vendus destination by category
    create_or_update(
        ctx, 'product.putaway', '__setup__.stock_putaway_onorder', {
            'name': 'Achetés-Vendus',
            'method': 'fixed',
        })
    onorders = [
        ('__setup__.stock_putaway_strat_onorder_ali',
         'specific_data.product_categ_ali',
         '__setup__.stock_location_order_ali'),
        ('__setup__.stock_putaway_strat_onorder_medoc',
         'specific_data.product_categ_medoc',
         '__setup__.stock_location_order_medoc'),
        ('__setup__.stock_putaway_strat_onorder_frigo',
         'specific_data.product_categ_frigo',
         '__setup__.stock_location_order_frigo'),
        ('__setup__.stock_putaway_strat_onorder_mat',
         'specific_data.product_categ_materiel',
         '__setup__.stock_location_order_mat'),
    ]
    for xmlid, categ, loc in onorders:
        create_or_update(
            ctx, 'stock.fixed.putaway.strat', xmlid,
            {
                'putaway_id': ref('__setup__.stock_putaway_onorder').id,
                'category_id': ref(categ).id,
                'fixed_location_id': ref(loc).id,
            }
        )
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_onorder',
        {
            'putaway_strategy_id': ref('__setup__.stock_putaway_onorder').id
        })


@anthem.log
def create_picking_types(ctx):
    """ Creating picking types """
    wh = ctx.env.ref('stock.warehouse0')
    picking_sequence = wh.pick_type_id.sequence_id
    delivery_sequence = wh.out_type_id.sequence_id
    internal_sequence = wh.int_type_id.sequence_id

    location_stock = ctx.env.ref('stock.stock_location_stock')
    location_out = ctx.env.ref('stock.stock_location_output')
    location_mat = ctx.env.ref('__setup__.stock_location_materiel')
    location_ali = ctx.env.ref('__setup__.stock_location_ali')
    location_medoc = ctx.env.ref('__setup__.stock_location_medoc')
    location_froid = ctx.env.ref('__setup__.stock_location_froid')
    location_frigo = ctx.env.ref('__setup__.stock_location_frigo')
    location_parking_medoc = ctx.env.ref(
        '__setup__.stock_location_parking_medoc')
    location_parking_ali = ctx.env.ref(
        '__setup__.stock_location_parking_ali')
    location_parking_materiel = ctx.env.ref(
        '__setup__.stock_location_parking_materiel')
    location_parking_frigo = ctx.env.ref(
        '__setup__.stock_location_parking_frigo')
    location_reserve_medoc = ctx.env.ref(
        '__setup__.stock_location_reserve_medoc')
    location_reserve_ali = ctx.env.ref('__setup__.stock_location_reserve_ali')
    location_retours = ctx.env.ref('__setup__.stock_location_return')
    location_supplier = ctx.env.ref('stock.stock_location_suppliers')
    location_casse = ctx.env.ref('__setup__.stock_location_destroy')
    location_pharma = ctx.env.ref('__setup__.stock_location_pharma')
    location_detruit = ctx.env.ref('__setup__.stock_location_destroyed')

    color_ali = 2
    color_mat = 4
    color_froid = 6
    color_medoc = 7
    color_back = 8

    types = [
        {'xmlid': 'stock.picking_type_in',
         'use_create_lots': False,
         'use_existing_lots': True,
         'subcode': 'RECEIVE',
         },
        {'xmlid': '__setup__.stock_picking_type_materiel',
         'name': 'Pick Matériel',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_mat.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         'subcode': 'PICK',
         'groupbypartner': True,
         'color': color_mat,
         'sequence': 6,
         'zone_code': '02',
         },
        {'xmlid': '__setup__.stock_picking_type_ali',
         'name': 'Pick Aliments',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_ali.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         'subcode': 'PICK',
         'groupbypartner': True,
         'color': color_ali,
         'sequence': 5,
         'zone_code': '04',
         'food_type': True,
         },
        {'xmlid': '__setup__.stock_picking_type_medoc',
         'name': 'Pick Médicaments',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_stock.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         'subcode': 'PICK',
         'groupbypartner': True,
         'color': color_medoc,
         'sequence': 4,
         'zone_code': '01',
         },
        {'xmlid': '__setup__.stock_picking_type_froid',
         'name': 'Pick Frigo',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_froid.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         'subcode': 'PICK',
         'groupbypartner': True,
         'color': color_froid,
         'sequence': 7,
         'zone_code': '03',
         },
        {'xmlid': '__setup__.stock_picking_type_humain',
         'name': 'Pick Humain',
         'code': 'internal',
         'sequence_id': picking_sequence.id,
         'default_location_src_id': location_pharma.id,
         'default_location_dest_id': location_out.id,
         'use_create_lots': False,
         'subcode': 'PICK',
         'groupbypartner': True,
         'color': color_mat,
         'sequence': 8,
         'zone_code': '05',
         },

        {'xmlid': '__setup__.stock_picking_type_rangement_medoc',
         'name': 'Rangement Medicaments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_medoc.id,
         'default_location_dest_id': location_medoc.id,
         'use_create_lots': False,
         'color': color_medoc,
         'sequence': 9,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_ali',
         'name': 'Rangement Aliments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_ali.id,
         'default_location_dest_id': location_ali.id,
         'use_create_lots': False,
         'color': color_ali,
         'sequence': 9,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_materiel',
         'name': 'Rangement Matériel',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_materiel.id,
         'default_location_dest_id': location_mat.id,
         'use_create_lots': False,
         'color': color_mat,
         'sequence': 9,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_frigo',
         'name': 'Rangement Frigo',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_frigo.id,
         'default_location_dest_id': location_frigo.id,
         'use_create_lots': False,
         'color': color_froid,
         'sequence': 9,
         },

        {'xmlid': '__setup__.stock_picking_type_reassort_medoc',
         'name': 'Reassort Medicaments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_reserve_medoc.id,
         'default_location_dest_id': location_medoc.id,
         'use_create_lots': False,
         'color': color_medoc,
         'sequence': 10,
         },
        {'xmlid': '__setup__.stock_picking_type_reassort_ali',
         'name': 'Reassort Aliments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_reserve_ali.id,
         'default_location_dest_id': location_ali.id,
         'use_create_lots': False,
         'color': color_ali,
         'sequence': 11,
         },
        {'xmlid': '__setup__.stock_picking_type_return',
         'name': 'Retours',
         'code': 'outgoing',
         'sequence_id': delivery_sequence.id,
         'default_location_src_id': location_retours.id,
         'default_location_dest_id': location_supplier.id,
         'use_create_lots': False,
         'color': color_back,
         'sequence': 12,
         },
        {'xmlid': '__setup__.stock_picking_type_destroy',
         'name': 'Destructions',
         'code': 'outgoing',
         'sequence_id': delivery_sequence.id,
         'default_location_src_id': location_casse.id,
         'default_location_dest_id': location_detruit.id,
         'use_create_lots': False,
         'color': color_back,
         'sequence': 13,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'stock.picking.type', xmlid, record)

    create_or_update(ctx, 'stock.picking.type', 'stock.picking_type_in', {
        'default_location_dest_id': ctx.env.ref(
            'stock.stock_location_company').id
    })


@anthem.log
def create_procurement_rules(ctx):
    """ Creating procurement rules """
    ref = ctx.env.ref
    location_out = ref('stock.stock_location_output')
    warehouse = ctx.env.ref('stock.warehouse0')
    types = [
        {'xmlid': '__setup__.procurement_rule_materiel',
         'sequence': 15,
         'name': 'WH: Stock -> Output (MAT)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__setup__.stock_location_materiel').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_ali',
         'sequence': 15,
         'name': 'WH: Stock -> Output (ALI)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__setup__.stock_location_ali').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_medoc',
         'sequence': 15,
         'name': 'WH: Stock -> Output (MED)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_froid',
         'sequence': 15,
         'name': 'WH: Stock -> Output (FRIGO)',
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('__setup__.stock_location_froid').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
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
        {'xmlid': '__setup__.stock_location_route_pick_materiel',
         'name': 'Alcyon Belux SA: Pick (MAT)',
         'pull_ids': [(6, 0, ref('__setup__.procurement_rule_materiel').ids)],
         },
        {'xmlid': '__setup__.stock_location_route_pick_ali',
         'name': 'Alcyon Belux SA: Pick (ALI)',
         'pull_ids': [(6, 0, ref('__setup__.procurement_rule_ali').ids)],
         },
        {'xmlid': '__setup__.stock_location_route_pick_medoc',
         'name': 'Alcyon Belux SA: Pick (MED)',
         'pull_ids': [(6, 0, ref('__setup__.procurement_rule_medoc').ids)],
         },
        {'xmlid': '__setup__.stock_location_route_pick_froid',
         'name': 'Alcyon Belux SA: Pick (FROID)',
         'pull_ids': [(6, 0, ref('__setup__.procurement_rule_froid').ids)],
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
    categs = [('specific_data.product_categ_materiel',
               '__setup__.stock_location_route_pick_materiel'),
              ('specific_data.product_categ_ali',
               '__setup__.stock_location_route_pick_ali'),
              ('specific_data.product_categ_medoc',
               '__setup__.stock_location_route_pick_medoc'),
              ('specific_data.product_categ_frigo',
               '__setup__.stock_location_route_pick_froid'),
              ]
    for category_xmlid, route_xmlid in categs:
        ref(category_xmlid).route_ids = [(6, 0, ref(route_xmlid).ids)]


@anthem.log
def main(ctx):
    """ Configuring logistics """
    company_settings(ctx)
    activate_options(ctx)
    set_delivery_pick_ship(ctx)
    create_locations(ctx)
    create_putaway(ctx)
    create_picking_types(ctx)
    create_procurement_rules(ctx)
    create_routes(ctx)
    assign_route_categories(ctx)
