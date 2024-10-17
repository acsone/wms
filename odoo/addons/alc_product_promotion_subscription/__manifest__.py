# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Product Promotion Subscription",
    "description": """
        Alcyon: Manage parter's subscriptions to producvt promotion""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "product",
        "sales_team",
        # Third-party
        "partner_manual_rank",
        # Alcyon/Sales Management
        "alc_pricelist_discount",
    ],
    "data": [
        "security/alc_product_promotion_subscription.xml",
        "views/res_partner.xml",
        "views/alc_product_promotion_subscription.xml",
    ],
    "demo": [],
}
