# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Alc Sale Stock Loyalty Year End Rebate Coupon View",
    "summary": """Alcyon: Add rfa info into coupon view""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu",
    "depends": [
        # Alcyon
        "alc_sale_loyalty_coupon_point_view",
        "alc_sale_stock_loyalty_year_end_rebate",
    ],
    "data": ["views/sale_order_coupon_points.xml"],
    "demo": [],
}
