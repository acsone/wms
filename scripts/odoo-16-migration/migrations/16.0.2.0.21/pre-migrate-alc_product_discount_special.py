from openupgradelib import openupgrade


def migrate(cr, version):
    openupgrade.update_module_moved_models(
        cr,
        "product.discount.special",
        "product_discount_specials",
        "alc_product_discount_special",
    )
    openupgrade.update_module_moved_fields(
        cr,
        "product.template",
        ("product_discount_special_ids",),
        "product_discount_specials",
        "alc_product_discount_special",
    )
