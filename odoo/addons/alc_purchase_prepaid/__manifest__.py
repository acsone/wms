# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Alc Purchase Prepaid",
    "description": "Allow to mark a PO for prepayment",
    "version": "16.0.1.0.0",
    "author": "BCIM, ACSONE SA/NV",
    "category": "Purchases",
    "depends": [
        # Others
        "purchase",
    ],
    "data": ["views/purchase_order_views.xml"],
    "installable": True,
    "auto_install": False,
    "license": "AGPL-3",
}
