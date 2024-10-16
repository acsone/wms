# Copyright 2016-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Product Qty Unavailable",
    "version": "16.0.1.0.0",
    "summary": """"Adds product_qty_unavailable and current_product_qty_unavailable
                   on SO line""",
    "author": "BCIM, ACSONE SA/NV",
    "depends": [
        # Odoo Community
        "sale_stock",
        # Third-party
        "sale_order_line_cancel",
        "stock_available",
        # Alcyon
        "alc_base_auto_join",
    ],
    "data": ["views/sale_order_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
