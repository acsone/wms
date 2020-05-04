# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Delivery Rounds",
    "version": "1.1",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "category": "Stock Management",
    "depends": [
        "stock",
        "delivery",
        "stock_picking_assignment",
        "stock_picking_backorder",
        "stock_picking_subcode",
        "stock_picking_sequence",
        "stock_groupbypartner",
        "partner_delivery",
        "partner_schedule",
        "queue_job",
        "web_notify",
    ],
    "data": [
        # Views
        "views/menu.xml",
        "views/version.xml",
        "views/template.xml",
        "views/itinerary.xml",
        "views/instance.xml",
        "views/picking.xml",
        "views/partner.xml",
        "views/delivery_carrier.xml",
        "views/tag.xml",
        "views/cron_delivery_plan.xml",
        # Qweb
        "views/round_customer_report.xml",
        # Data
        "data/ir_cron.xml",
        "data/delivery_carrier.xml",
        # Security
        "security/ir.model.access.csv",
        # Wizards
        "wizards/instance_itinerary_import.xml",
        "wizards/make_today_delivery_plan.xml",
        "wizards/picking_assign_delivery_round.xml",
        # Static
        "views/style.xml",
    ],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
    "application": False,
}
