# © 2017 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Sale Consignment",
    "version": "16.0.1.0.0",
    "author": "Camptocamp,ACSONE SA/NV",
    "license": "AGPL-3",
    "category": "Stock Management",
    "depends": [
        # OCA
        "stock_override_procurement",
        # Others
        "sale_stock",
    ],
    "data": ["views/res_partner.xml", "views/sale_order.xml", "data/data.xml"],
    "pre_init_hook": "pre_init_hook",
}
