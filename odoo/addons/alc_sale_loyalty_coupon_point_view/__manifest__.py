# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Loyalty Coupon Point View",
    "summary": """Alcyon: Add view to get access to 'sale.order.coupon.points'""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Odoo Community
        "sale_loyalty",
        # Third-party
        "sale_loyalty_beneficiary",
    ],
    "data": [
        "views/sale_order_coupon_points.xml",
    ],
    "demo": [],
}
