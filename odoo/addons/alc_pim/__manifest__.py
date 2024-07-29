# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Alc PIM",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://acsone.eu/",
    "description": """Data for product categories, attributes and brands""",
    "depends": [
        # fmt: off
        # Custom
        "alc_pim_attribute_group",
        "alc_pim_attribute_group",
        "alc_pim_product",
        "alc_product_animal_species",
        "alc_product_audit",
        "alc_product_category_translatable",
        "alc_product_link_notice",
        "alc_product_shop_category",
        # OCA
        "product_brand",
        # fmt: on
    ],
    "application": False,
    "data": [
        "data/product_category.xml",
        "data/attribute_attribute.xml",
        "data/attribute_option.xml",
        "data/product_brand.xml",
    ],
    "demo": [],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
}
