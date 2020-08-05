# -*- coding: utf-8 -*-
# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Consignment",
    "version": "10.0.1.0.0",
    "author": "BCIM",
    "maintainer": "Camptocamp",
    "license": "AGPL-3",
    "category": "Stock Management",
    "depends": ["sale_stock", "sale_cancel_remaining", "product_additional"],
    "data": ["views/res_partner.xml", "views/sale.xml", "data/data.xml"],
    "installable": True,
}
