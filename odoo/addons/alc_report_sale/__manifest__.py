# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc Report Sale",
    "summary": """
        Sale reporting for Alcyon""",
    "version": "16.0.1.0.5",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "depends": [
        # Odoo Community
        "sale",
        # Third-party
        "sale_triple_discount",
        # Alcyon
        "alc_accounting_data",
        "alc_partner_pharmacist",
        "alc_partner_veterinary",
        "alc_product_pharmacy",
        "alc_report_base",
        "alc_sale_suite_name",
        # Alcyon/Stock Management
        "alc_sale_consignment",
    ],
    "data": [
        "views/report_saleorder_document.xml",
        "views/res_config_settings.xml",
        "data/mail_template.xml",
    ],
    "demo": [],
    "installable": True,
}
