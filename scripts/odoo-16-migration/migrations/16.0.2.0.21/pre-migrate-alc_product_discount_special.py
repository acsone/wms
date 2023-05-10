from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.update_module_moved_models(
        env.cr,
        "product.discount.special",
        "product_discount_specials",
        "alc_product_discount_special",
    )
    openupgrade.update_module_moved_fields(
        env.cr,
        "product.template",
        ("product_discount_special_ids",),
        "product_discount_specials",
        "alc_product_discount_special",
    )
