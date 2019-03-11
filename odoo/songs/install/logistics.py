# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem
from pkg_resources import resource_stream
from anthem.lyrics.records import create_or_update
from anthem.lyrics.loaders import load_csv_stream

from ..common import req
from ..common import define_settings

# Assignment types
PICKING_ASSIGNMENT = '1'
RANGEMENT_ASSIGNMENT = '2'
REASSORT_ASSIGNMENT = '3'


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
def settings_lot_base_date(ctx):
    """ Set product life date as base date """

    # Default invoice
    define_settings(ctx,
                    'stock.config.settings',
                    {'production_lot_base_date': 'life'})


@anthem.log
def activate_options(ctx):
    """ Activating logistics options """
    employee_group = ctx.env.ref('base.group_user')
    employee_group.write({
        'implied_ids':
            [(4, ctx.env.ref('stock.group_production_lot').id),
             (4, ctx.env.ref('stock.group_stock_multi_locations').id),
             (4, ctx.env.ref('stock.group_adv_location').id),
             (4, ctx.env.ref('stock.group_tracking_lot').id)]

    })


@anthem.log
def warehouse_settings(ctx):
    wh_vlb = ctx.env.ref('stock.warehouse0')
    wh_vlb.write({
        'name': 'Villers-Le-Bouillet',
        'code': 'VLB',
        'delivery_steps': 'pick_ship',
    })


@anthem.log
def create_picking_zones(ctx):
    """ Creating picking zones """
    content = resource_stream(req, 'data/install/picking.zone.csv')
    load_csv_stream(ctx, 'picking.zone', content, delimiter=',')


@anthem.log
def create_locations(ctx):
    """ Creating stock locations """
    load_ctx = ctx.env.context.copy()
    load_ctx.update({'defer_parent_store_computation': 'manually'})
    Location = ctx.env['stock.location'].with_context(load_ctx)
    loc_stock = ctx.env.ref('stock.stock_location_stock')
    # root = ctx.env.ref('stock.stock_location_locations')
    loc_partner = ctx.env.ref('stock.stock_location_locations_partner')

    # Change the parent of the location Output (VLB to Physical Locations)
    ctx.env.ref('stock.stock_location_output').write({
        'location_id': ctx.env.ref('stock.stock_location_locations').id
    })

    # Input
    create_or_update(ctx, Location, 'stock.stock_location_company', {
        'usage': 'internal',
        'active': True,
    })

    # Retours Client
    create_or_update(
        ctx, Location, '__setup__.stock_location_customers_return', {
            'name': 'Clients (retours)',
            'location_id': loc_partner.id,
            'usage': 'supplier',
        })

    # Reserves = Products available => under WH, above Stock
    reserves = [
        ('__setup__.stock_location_reserve_ali', 'Réserve Aliments',
         loc_stock.location_id.id),
        ('__setup__.stock_location_reserve_medoc', 'Réserve Médicaments',
         loc_stock.location_id.id),
    ]
    for xmlid, name, location_id in reserves:
        create_or_update(ctx, Location, xmlid, {
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
        create_or_update(ctx, Location, xmlid, {
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
        create_or_update(ctx, Location, xmlid, {
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
        ),
        (
            '__setup__.stock_location_parking_ali',
            'Parking Aliments',
        ),
        (
            '__setup__.stock_location_parking_materiel',
            'Parking Matériel',
        ),
        (
            '__setup__.stock_location_parking_frigo',
            'Parking Frigo',
        ),
    ]
    for xmlid, name in parkings:
        create_or_update(ctx, Location, xmlid, {
            'name': name,
            'location_id': ctx.env.ref('stock.stock_location_company').id,
            'usage': 'view',
            'kind': 'parking',
        })

    # Achetés-Vendus is under Input (part of stock)
    create_or_update(
        ctx, Location, '__setup__.stock_location_onorder',
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
        create_or_update(ctx, Location, xmlid, {
            'name': name,
            'location_id': ctx.env.ref('__setup__.stock_location_onorder').id,
            'usage': 'view',
        })

    # Nouveautés is under Input (part of stock)
    create_or_update(
        ctx, Location, '__setup__.stock_location_new',
        {
            'name': 'Nouveautés',
            'location_id': ctx.env.ref('stock.stock_location_company').id,
            'usage': 'view',
        })
    news = [
        ('__setup__.stock_location_new_ali', 'Nouveautés Aliments'),
        ('__setup__.stock_location_new_medoc', 'Nouveautés Médicaments'),
        ('__setup__.stock_location_new_frigo', 'Nouveautés Frigo'),
        ('__setup__.stock_location_new_mat', 'Nouveautés Matériel'),
    ]
    for xmlid, name in news:
        create_or_update(ctx, Location, xmlid, {
            'name': name,
            'location_id': ctx.env.ref('__setup__.stock_location_new').id,
            'usage': 'view',
        })

    # Casse = Products unavailable => not under physical locations
    create_or_update(
        ctx, Location, 'stock.stock_location_scrapped', {
            'name': 'Scrap',
            'location_id': False,
            'usage': 'view',
            'scrap_location': False,
        })
    scrap = [
        ('__setup__.stock_location_scrap_destroy', 'A détruire', 0, 0),
        ('__setup__.stock_location_scrap_quality', 'Problème Qualité', 0, 1),
        ('__setup__.stock_location_scrap_return', 'Retours Fournisseur', 1, 0),
        ]
    for xmlid, name, accrued_supplier_return, is_scrap in scrap:
        create_or_update(ctx, Location, xmlid, {
            'name': name,
            'location_id': ctx.env.ref('stock.stock_location_scrapped').id,
            'usage': 'internal',
            'ignore_quants_expiration': True,
            'scrap_location': is_scrap,
            'accrued_supplier_return': accrued_supplier_return,
        })

    loc_partner = ctx.env.ref('stock.stock_location_locations_partner')
    create_or_update(
        ctx, Location, '__setup__.stock_location_destroyed', {
            'name': 'Détruit',
            'location_id': loc_partner.id,
            'usage': 'customer',
        })

    # Create a location for migrated Sales
    create_or_update(
        ctx, Location, '__setup__.mig_sale_pick',
        {
            'name': '[MIGRATION] Stock ventes',
            'usage': 'customer',
            'active': True,
        })
    # Create a location for migrated Purchases
    create_or_update(
        ctx, Location, '__setup__.mig_purchase_reception',
        {
            'name': '[MIGRATION] Réception achats',
            'usage': 'supplier',
            'active': True,
        })
    Location._parent_store_compute()


@anthem.log
def set_helpdesk_reason_location(ctx):
    ref = ctx.env.ref
    scrap = ref('__setup__.stock_location_scrap_quality')
    ref('specific_helpdesk.product_defect').location_dest_id = scrap.id
    ref('specific_helpdesk.cold_chain_broken').location_dest_id = scrap.id
    ref('specific_helpdesk.expired_product').location_dest_id = scrap.id


@anthem.log
def create_putaway(ctx):
    """ Create putaway and putaway strat
    """
    ref = ctx.env.ref

    loc_stock_id = ref('stock.stock_location_stock').id

    # PUTAWAY INPUT
    # -------------
    create_or_update(ctx, 'product.putaway', '__setup__.stock_putaway_input', {
        'name': 'Input',
        'method': 'fixed',
        'fixed_location_id': loc_stock_id,
    })
    # Fixed Locations Per Routes
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_mto',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('stock.route_warehouse0_mto').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_onorder').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_new',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('__setup__.stock_location_route_new').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_new').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_ali',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('__setup__.stock_location_route_pick_ali').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_parking_ali').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_med',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('__setup__.stock_location_route_pick_medoc').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_parking_medoc').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_mat',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('__setup__.stock_location_route_pick_materiel').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_parking_materiel').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_input_froid',
        {
            'putaway_id': ref('__setup__.stock_putaway_input').id,
            'route_id': ref('__setup__.stock_location_route_pick_froid').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_parking_frigo').id,
        }
    )
    # Fixed Locations Per Categories
    parking_strat = [
        ('__setup__.stock_putaway_strat_parking_medoc',
         'specific_data.product_categ_medoc',
         '__setup__.stock_location_parking_medoc'),
        ('__setup__.stock_putaway_strat_parking_aliment',
         'specific_data.product_categ_ali',
         '__setup__.stock_location_parking_ali'),
        ('__setup__.stock_putaway_strat_parking_materiel',
         'specific_data.product_categ_materiel',
         '__setup__.stock_location_parking_materiel'),
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
    # Assign putaway to Input location
    create_or_update(ctx, 'stock.location', 'stock.stock_location_company', {
        'location_id': loc_stock_id,
        'putaway_strategy_id': ref('__setup__.stock_putaway_input').id
    })

    # PUTAWAY ACHETES-VENDUS
    # ----------------------
    create_or_update(
        ctx, 'product.putaway', '__setup__.stock_putaway_onorder', {
            'name': 'Achetés-Vendus',
            'method': 'fixed',
        })
    # Fixed Locations Per Routes
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_onorder_ali',
        {
            'putaway_id': ref('__setup__.stock_putaway_onorder').id,
            'route_id': ref('__setup__.stock_location_route_pick_ali').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_order_ali').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_onorder_med',
        {
            'putaway_id': ref('__setup__.stock_putaway_onorder').id,
            'route_id': ref('__setup__.stock_location_route_pick_medoc').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_order_medoc').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_onorder_mat',
        {
            'putaway_id': ref('__setup__.stock_putaway_onorder').id,
            'route_id': ref('__setup__.stock_location_route_pick_materiel').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_order_mat').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_onorder_froid',
        {
            'putaway_id': ref('__setup__.stock_putaway_onorder').id,
            'route_id': ref('__setup__.stock_location_route_pick_froid').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_order_frigo').id,
        }
    )
    # Fixed Locations Per Categories
    onorders = [
        ('__setup__.stock_putaway_strat_onorder_ali',
         'specific_data.product_categ_ali',
         '__setup__.stock_location_order_ali'),
        ('__setup__.stock_putaway_strat_onorder_medoc',
         'specific_data.product_categ_medoc',
         '__setup__.stock_location_order_medoc'),
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
    # Assign putaway to Achetés-Vendus location
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_onorder',
        {
            'putaway_strategy_id': ref('__setup__.stock_putaway_onorder').id
        })

    # PUTAWAY NOUVEAUTES
    # ------------------
    create_or_update(
        ctx, 'product.putaway', '__setup__.stock_putaway_new', {
            'name': 'Nouveautés',
            'method': 'fixed',
        })
    # Fixed Locations Per Routes
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_new_ali',
        {
            'putaway_id': ref('__setup__.stock_putaway_new').id,
            'route_id': ref('__setup__.stock_location_route_pick_ali').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_new_ali').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_new_med',
        {
            'putaway_id': ref('__setup__.stock_putaway_new').id,
            'route_id': ref('__setup__.stock_location_route_pick_medoc').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_new_medoc').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_new_mat',
        {
            'putaway_id': ref('__setup__.stock_putaway_new').id,
            'route_id': ref('__setup__.stock_location_route_pick_materiel').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_new_mat').id,
        }
    )
    create_or_update(
        ctx, 'stock.fixed.putaway.route.strat',
        '__setup__.stock_putaway_new_froid',
        {
            'putaway_id': ref('__setup__.stock_putaway_new').id,
            'route_id': ref('__setup__.stock_location_route_pick_froid').id,
            'fixed_location_id': ref(
                '__setup__.stock_location_new_frigo').id,
        }
    )
    # Fixed Locations Per Categories
    news = [
        ('__setup__.stock_putaway_strat_new_ali',
         'specific_data.product_categ_ali',
         '__setup__.stock_location_new_ali'),
        ('__setup__.stock_putaway_strat_new_medoc',
         'specific_data.product_categ_medoc',
         '__setup__.stock_location_new_medoc'),
        ('__setup__.stock_putaway_strat_new_mat',
         'specific_data.product_categ_materiel',
         '__setup__.stock_location_new_mat'),
    ]
    for xmlid, categ, loc in news:
        create_or_update(
            ctx, 'stock.fixed.putaway.strat', xmlid,
            {
                'putaway_id': ref('__setup__.stock_putaway_new').id,
                'category_id': ref(categ).id,
                'fixed_location_id': ref(loc).id,
            }
        )
    # Assign putaway to Nouveautés location
    create_or_update(
        ctx, 'stock.location', '__setup__.stock_location_new',
        {
            'putaway_strategy_id': ref('__setup__.stock_putaway_new').id
        })


@anthem.log
def create_picking_types(ctx):
    """ Creating picking types """
    wh = ctx.env.ref('stock.warehouse0')
    reception_sequence = wh.in_type_id.sequence_id
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
    location_supplier = ctx.env.ref('stock.stock_location_suppliers')
    location_customers_return = ctx.env.ref(
        '__setup__.stock_location_customers_return')
    location_in_return = ctx.env.ref('stock.stock_location_company')
    location_scrap = ctx.env.ref('stock.stock_location_scrapped')
    location_scrap_quality = ctx.env.ref(
        '__setup__.stock_location_scrap_quality')
    location_scrap_return = ctx.env.ref(
        '__setup__.stock_location_scrap_return')
    location_destroyed = ctx.env.ref('__setup__.stock_location_destroyed')
    location_to_destroy = ctx.env.ref('__setup__.stock_location_scrap_destroy')

    color_mrp = 0
    color_in = 1
    color_rangement = 2
    color_reassort = 3
    color_internal = 4
    color_pick = 5
    color_scrap = 6
    color_quality = 7
    color_out = 8

    types = [
        {'xmlid': 'stock.picking_type_in',
         'name': u'Réception des achats',
         'use_create_lots': False,
         'use_existing_lots': True,
         'subcode': 'RECEIVE',
         'color': color_in,
         'sequence': 10,
         },
        {'xmlid': '__setup__.picking_type_in_return',
         'name': 'Retours Client',
         'code': 'incoming',
         'sequence_id': reception_sequence.id,
         'default_location_src_id': location_customers_return.id,
         'default_location_dest_id': location_in_return.id,
         'use_create_lots': False,
         'use_existing_lots': True,
         'subcode': 'RECEIVE',
         'color': color_in,
         'sequence': 20,
         'create_invoice_on_transfer': True,
         },

        {'xmlid': '__setup__.stock_picking_type_rangement_medoc',
         'name': 'Rangement Medicaments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_medoc.id,
         'default_location_dest_id': location_medoc.id,
         'use_create_lots': False,
         'color': color_rangement,
         'sequence': 30,
         'picking_zone_id': ctx.env.ref(
             '__setup__.picking_zone_medicament').id,
         'zetes_picking_type': RANGEMENT_ASSIGNMENT,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_ali',
         'name': 'Rangement Aliments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_ali.id,
         'default_location_dest_id': location_ali.id,
         'use_create_lots': False,
         'color': color_rangement,
         'sequence': 31,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_aliments').id,
         'zetes_picking_type': RANGEMENT_ASSIGNMENT,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_materiel',
         'name': 'Rangement Matériel',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_materiel.id,
         'default_location_dest_id': location_mat.id,
         'use_create_lots': False,
         'color': color_rangement,
         'sequence': 32,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_materiel').id,
         'zetes_picking_type': RANGEMENT_ASSIGNMENT,
         },
        {'xmlid': '__setup__.stock_picking_type_rangement_frigo',
         'name': 'Rangement Frigo',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_parking_frigo.id,
         'default_location_dest_id': location_frigo.id,
         'use_create_lots': False,
         'color': color_rangement,
         'sequence': 33,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_frigo').id,
         'zetes_picking_type': RANGEMENT_ASSIGNMENT,
         },

        {'xmlid': '__setup__.stock_picking_type_reassort_medoc',
         'name': 'Reassort Medicaments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_reserve_medoc.id,
         'default_location_dest_id': location_medoc.id,
         'use_create_lots': False,
         'color': color_reassort,
         'sequence': 40,
         'picking_zone_id': ctx.env.ref(
             '__setup__.picking_zone_medicament').id,
         'zetes_picking_type': REASSORT_ASSIGNMENT,
         },
        {'xmlid': '__setup__.stock_picking_type_reassort_ali',
         'name': 'Reassort Aliments',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_reserve_ali.id,
         'default_location_dest_id': location_ali.id,
         'use_create_lots': False,
         'color': color_reassort,
         'sequence': 41,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_aliments').id,
         'zetes_picking_type': REASSORT_ASSIGNMENT,
         },

        {'xmlid': 'stock.picking_type_internal',
         'active': True,
         'sequence': 50,
         'color': color_internal,
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
         'color': color_pick,
         'sequence': 60,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_materiel').id,
         'zetes_picking_type': PICKING_ASSIGNMENT,
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
         'color': color_pick,
         'sequence': 61,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_aliments').id,
         'is_portable_printer': True,
         'zetes_picking_type': PICKING_ASSIGNMENT,
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
         'color': color_pick,
         'sequence': 62,
         'picking_zone_id': ctx.env.ref(
             '__setup__.picking_zone_medicament').id,
         'zetes_picking_type': PICKING_ASSIGNMENT,
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
         'color': color_pick,
         'sequence': 63,
         'picking_zone_id': ctx.env.ref('__setup__.picking_zone_frigo').id,
         'zetes_picking_type': PICKING_ASSIGNMENT,
         },

        {'xmlid': 'stock_expired.picking_type_scrap',
         'color': color_scrap,
         'sequence': 70,
         'default_location_dest_id': location_scrap_quality.id,
         },

        {'xmlid': '__setup__.stock_scrap_quality',
         'name': 'Qualité Scrap - Casse',
         'code': 'internal',
         'sequence_id': internal_sequence.id,
         'default_location_src_id': location_scrap_quality.id,
         'default_location_dest_id': location_scrap.id,
         'use_create_lots': False,
         'color': color_quality,
         'sequence': 80,
         },

        {'xmlid': 'stock.picking_type_out',
         'active': True,
         'groupbypartner': True,
         'color': color_out,
         'sequence': 90,
         'create_invoice_on_transfer': True,
         },
        {'xmlid': '__setup__.stock_picking_type_return',
         'name': 'Retours fournisseur',
         'code': 'outgoing',
         'sequence_id': delivery_sequence.id,
         'default_location_src_id': location_scrap_return.id,
         'default_location_dest_id': location_supplier.id,
         'use_create_lots': False,
         'color': color_out,
         'sequence': 91,
         },
        {'xmlid': '__setup__.stock_picking_type_destroy',
         'name': 'Destructions',
         'code': 'outgoing',
         'sequence_id': delivery_sequence.id,
         'default_location_src_id': location_to_destroy.id,
         'default_location_dest_id': location_destroyed.id,
         'use_create_lots': False,
         'color': color_out,
         'sequence': 92,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'stock.picking.type', xmlid, record)

    create_or_update(ctx, 'stock.picking.type', 'stock.picking_type_in', {
        'default_location_dest_id': ctx.env.ref(
            'stock.stock_location_company').id
    })
    ctx.env['stock.picking.type'].search([('name', '=', 'Pick')]).write({
        'subcode': 'PICK',
        'sequence': 59,
        'color': color_pick,
        })
    ctx.env['stock.picking.type'].search([('code', '=', 'mrp_operation')])\
        .write({
            'sequence': 89,
            'color': color_mrp,
            })


@anthem.log
def create_fix_delivery_picking_type(ctx):
    """create a new picking type to be used for the pickings to fix.

    use self.env.ref('__setup__.stock_picking_type_fix_ship') to acces it.
    """
    ptype = ctx.env.ref(
        '__setup__.stock_picking_type_fix_ship',
        raise_if_not_found=False
    )
    if ptype:  # make sure script is idempotent
        return ptype
    ship = ctx.env.ref('stock.picking_type_out')
    ptype = ship.copy({'name': 'Correction pb livraison'})
    ctx.env['ir.model.data'].create(
        {'name': 'stock_picking_type_fix_ship',
         'module': '__setup__',
         'model': 'stock.picking.type',
         'res_id': ptype.id,
         }
    )
    return ptype


@anthem.log
def configure_procurement_rules(ctx):
    """
    Change the procurement location (VLB Stock -> VLB) for the BUY rules
    :param ctx:
    :return:
    """
    location_vlb_stock = ctx.env.ref('stock.stock_location_stock')
    # The location VLB doesn't have a XML ID
    location_vlb = location_vlb_stock.location_id

    rulesBuy = ctx.env['procurement.rule'].search([('action', '=', 'buy')])
    rulesBuy.write({
        'location_id': location_vlb.id
    })


@anthem.log
def create_procurement_rules(ctx):
    """ Creating procurement rules """
    ref = ctx.env.ref
    location_out = ref('stock.stock_location_output')
    warehouse = ctx.env.ref('stock.warehouse0')
    types = [
        {'xmlid': '__setup__.procurement_rule_materiel',
         'type': ['categ', 'prod', 'sale'],
         'name': 'WH: Stock -> Output (MAT)',
         'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
         },
        {'xmlid': '__setup__.procurement_rule_ali',
         'type': ['categ', 'prod', 'sale'],
         'name': 'WH: Stock -> Output (ALI)',
         'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
         },
        {'xmlid': '__setup__.procurement_rule_medoc',
         'type': ['categ', 'prod', 'sale'],
         'name': 'WH: Stock -> Output (MED)',
         'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
         },
        {'xmlid': '__setup__.procurement_rule_froid',
         'type': ['prod', 'sale'],
         'name': 'WH: Stock -> Output (FRIGO)',
         'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        types = record.pop('type')
        default_name = record.pop('name')
        record.update({
         'action': 'move',
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'procure_method': 'make_to_stock',
         'group_propagation_option': 'propagate',
        })
        sequences = {'categ': 15, 'prod': 10, 'sale': 0}
        for t in types:
            if t == 'sale':
                record['location_src_id'] = ref(
                    'stock.stock_location_company').id
            else:
                record['location_src_id'] = ref(
                    'stock.stock_location_stock').id
            record['name'] = default_name[:-1] + " - " + t.upper() + ")"
            record['sequence'] = sequences[t]
            create_or_update(ctx, 'procurement.rule',
                             '%s_%s' % (xmlid, t), record)


@anthem.log
def create_procurement_rules_mto(ctx):
    """ Creating procurement rules MTO """
    ref = ctx.env.ref
    location_out = ref('stock.stock_location_output')
    warehouse = ctx.env.ref('stock.warehouse0')
    types = [
        {'xmlid': '__setup__.procurement_rule_materiel_mto',
         'name': 'WH: Stock -> Output MTO (MAT)',
         'action': 'move',
         'sequence': 25,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_order',
         'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_ali_mto',
         'name': 'WH: Stock -> Output MTO (ALI)',
         'action': 'move',
         'sequence': 25,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_order',
         'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_medoc_mto',
         'name': 'WH: Stock -> Output MTO (MED)',
         'action': 'move',
         'sequence': 25,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_order',
         'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
         'group_propagation_option': 'propagate',
         },
        {'xmlid': '__setup__.procurement_rule_froid_mto',
         'name': 'WH: Stock -> Output MTO (FRIGO)',
         'action': 'move',
         'sequence': 25,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_order',
         'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
         'group_propagation_option': 'propagate',
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        create_or_update(ctx, 'procurement.rule', xmlid, record)


@anthem.log
def create_procurement_rules_mto_mts(ctx):
    """ Creating procurement rules MTO+MTS """
    ref = ctx.env.ref
    location_out = ref('stock.stock_location_output')
    warehouse = ctx.env.ref('stock.warehouse0')
    types = [
        {'xmlid': '__setup__.procurement_rule_materiel_mto_mtu',
         'name': 'WH: Stock -> Output MTO+MTS (MAT)',
         # 'action': 'split_procurement',
         'action': 'move',
         'sequence': 30,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_materiel').id,
         'group_propagation_option': 'propagate',
         'mts_rule_id':
             ctx.env.ref('__setup__.procurement_rule_materiel_prod').id,
         'mto_rule_id':
             ctx.env.ref('__setup__.procurement_rule_materiel_mto').id,
         },
        {'xmlid': '__setup__.procurement_rule_ali_mto_mtu',
         'name': 'WH: Stock -> Output MTO+MTS (ALI)',
         # 'action': 'split_procurement',
         'action': 'move',
         'sequence': 30,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_ali').id,
         'group_propagation_option': 'propagate',
         'mts_rule_id': ctx.env.ref('__setup__.procurement_rule_ali_prod').id,
         'mto_rule_id': ctx.env.ref('__setup__.procurement_rule_ali_mto').id,
         },
        {'xmlid': '__setup__.procurement_rule_medoc_mto_mtu',
         'name': 'WH: Stock -> Output MTO+MTS (MED)',
         # 'action': 'split_procurement',
         'action': 'move',
         'sequence': 30,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_medoc').id,
         'group_propagation_option': 'propagate',
         'mts_rule_id':
             ctx.env.ref('__setup__.procurement_rule_medoc_prod').id,
         'mto_rule_id': ctx.env.ref('__setup__.procurement_rule_medoc_mto').id,
         },
        {'xmlid': '__setup__.procurement_rule_froid_mto_mtu',
         'name': 'WH: Stock -> Output MTO+MTS (FRIGO)',
         # 'action': 'split_procurement',
         'action': 'move',
         'sequence': 30,
         'location_id': location_out.id,
         'warehouse_id': warehouse.id,
         'location_src_id': ref('stock.stock_location_stock').id,
         'procure_method': 'make_to_stock',
         'picking_type_id': ref('__setup__.stock_picking_type_froid').id,
         'group_propagation_option': 'propagate',
         'mts_rule_id':
             ctx.env.ref('__setup__.procurement_rule_froid_prod').id,
         'mto_rule_id': ctx.env.ref('__setup__.procurement_rule_froid_mto').id,
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
        {'xmlid': '__setup__.stock_location_route_pick_materiel_categ',
         'name': 'Zone Matériel (Categ)',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_materiel_categ').ids)],
         'product_categ_selectable': True,
         'product_selectable': False,
         },
        {'xmlid': '__setup__.stock_location_route_pick_materiel',
         'name': 'Zone Matériel',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_materiel_prod').ids)],
         'product_categ_selectable': False,
         'product_selectable': True,
         },

        {'xmlid': '__setup__.stock_location_route_pick_ali_categ',
         'name': 'Zone Aliments (Categ)',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_ali_categ').ids)],
         'product_categ_selectable': True,
         'product_selectable': False,
         },
        {'xmlid': '__setup__.stock_location_route_pick_ali',
         'name': 'Zone Aliments',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_ali_prod').ids)],
         'product_categ_selectable': False,
         'product_selectable': True,
         },

        {'xmlid': '__setup__.stock_location_route_pick_medoc_categ',
         'name': 'Zone Médicaments (Categ)',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_medoc_categ').ids)],
         'product_categ_selectable': True,
         'product_selectable': False,
         },
        {'xmlid': '__setup__.stock_location_route_pick_medoc',
         'name': 'Zone Médicaments',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_medoc_prod').ids)],
         'product_categ_selectable': False,
         'product_selectable': True,
         },

        {'xmlid': '__setup__.stock_location_route_pick_froid',
         'name': 'Zone FROID / FRIGO',
         'pull_ids': [
             (6, 0, ref('__setup__.procurement_rule_froid_prod').ids)],
         'product_selectable': True,
         },

        {'xmlid': '__setup__.stock_location_route_new',
         'name': 'Nouveauté',
         'product_categ_selectable': False,
         'product_selectable': True,
         },
    ]
    for record in types:
        xmlid = record.pop('xmlid')
        record.update({'sequence': 20})
        create_or_update(ctx, 'stock.location.route', xmlid, record)

    route_mto_values = {
        'pull_ids': [
            (6, 0, [ref('__setup__.procurement_rule_materiel_mto_mtu').id,
                    ref('__setup__.procurement_rule_ali_mto_mtu').id,
                    ref('__setup__.procurement_rule_medoc_mto_mtu').id,
                    ref('__setup__.procurement_rule_froid_mto_mtu').id])
        ]
    }

    create_or_update(
        ctx, 'stock.location.route',
        'stock.route_warehouse0_mto', route_mto_values
    )

    # Disable the route MTO+MTS
    create_or_update(ctx, 'stock.location.route',
                     'stock_mts_mto_rule.route_mto_mts',
                     {'product_selectable': False})

    # Create Sales BO route
    create_or_update(
        ctx, 'stock.location.route',
        '__setup__.stock_location_route_sale_bo',
        {'name': 'BO',
         'sequence': 0,
         'priority': 0,
         'product_categ_selectable': False,
         'product_selectable': False,
         'sale_selectable': True,
         'pull_ids': [
             (6, 0, [ref('__setup__.procurement_rule_ali_sale').id,
                     ref('__setup__.procurement_rule_medoc_sale').id,
                     ref('__setup__.procurement_rule_materiel_sale').id,
                     ref('__setup__.procurement_rule_froid_sale').id])],
         })


@anthem.log
def assign_route_categories(ctx):
    """ Assigning routes to product categories """
    ref = ctx.env.ref
    categs = [('specific_data.product_categ_materiel',
               '__setup__.stock_location_route_pick_materiel_categ'),
              ('specific_data.product_categ_ali',
               '__setup__.stock_location_route_pick_ali_categ'),
              ('specific_data.product_categ_medoc',
               '__setup__.stock_location_route_pick_medoc_categ'),
              ]
    for category_xmlid, route_xmlid in categs:
        ref(category_xmlid).route_ids = [(6, 0, ref(route_xmlid).ids)]


@anthem.log
def set_picking_zone(ctx):
    """ Set the picking zone on all picking locations and on products
    """
    main_locations_picking_zone_mapping = {
        '__setup__.stock_location_ali': '__setup__.picking_zone_aliments',
        '__setup__.stock_location_froid': '__setup__.picking_zone_frigo',
        '__setup__.stock_location_materiel': '__setup__.picking_zone_materiel',
        '__setup__.stock_location_medoc': '__setup__.picking_zone_medicament',
    }
    for main_location_xmlid, picking_zone_xml_id in \
            main_locations_picking_zone_mapping.iteritems():
        main_location = ctx.env.ref(main_location_xmlid)
        picking_zone_id = ctx.env.ref(picking_zone_xml_id)
        children = ctx.env['stock.location'].search([
            ('id', 'child_of', main_location.id)])
        (main_location | children).write({
            'picking_zone_id': picking_zone_id.id
        })

    # Recompute the picking zone on each products
    ctx.env['product.template'].search([])._compute_picking_zone_id()


@anthem.log
def set_product_expiry(ctx):
    """ Set the expiry delay on product categories """
    ctx.env['product.category'].search([]).write({
        'alert_time': 1,
        'removal_time': 91,
        'life_time': 121,
        })


@anthem.log
def main(ctx):
    """ Configuring logistics """
    company_settings(ctx)
    settings_lot_base_date(ctx)
    activate_options(ctx)
    warehouse_settings(ctx)
    create_picking_zones(ctx)
    create_locations(ctx)
    set_helpdesk_reason_location(ctx)
    create_picking_types(ctx)
    create_fix_delivery_picking_type(ctx)
    configure_procurement_rules(ctx)
    create_procurement_rules(ctx)
    create_procurement_rules_mto(ctx)
    create_procurement_rules_mto_mts(ctx)
    create_routes(ctx)
    create_putaway(ctx)
    assign_route_categories(ctx)
    set_product_expiry(ctx)


@anthem.log
def post_import_products(ctx):
    """ Configure products after they have been imported """
    set_picking_zone(ctx)
