# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


def migrate_shopinvader_variant(env):
    product_index_fr = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_variant_index_fr_BE"
    )
    product_index_nl = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_variant_index_nl_BE"
    )
    product_index_en = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_variant_index_en_US"
    )

    for product_index in [product_index_fr, product_index_nl, product_index_en]:
        _logger.info("Migrate shopinvader_variant for index %s", product_index.name)
        # create se_binding
        env.cr.execute(
            """
            INSERT INTO se_binding (
                backend_id,
                index_id,
                res_id,
                res_model,
                data,
                state,
                create_date,
                write_date,
                create_uid,
                write_uid,
                active
                )
            SELECT
                %(backend_id)s,
                %(index_id)s,
                shopinvader_variant.record_id,
                'product.product',
                to_jsonb(shopinvader_variant.data),
                'done',
                shopinvader_variant.create_date,
                shopinvader_variant.write_date,
                shopinvader_variant.create_uid,
                shopinvader_variant.write_uid,
                shopinvader_variant.active
            FROM
                shopinvader_variant
                JOIN shopinvader_product ON shopinvader_product.id = shopinvader_variant.shopinvader_product_id
            WHERE
                shopinvader_product.lang_id = %(lang_id)s
            """,
            {
                "backend_id": product_index.backend_id.id,
                "index_id": product_index.id,
                "lang_id": product_index.lang_id.id,
            },
        )
        _logger.info("%d se_binding created", env.cr.rowcount)

    # create


def migrate_shopinvader_category(env):
    category_index_fr = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_category_index_fr_BE"
    )
    category_index_nl = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_category_index_nl_BE"
    )
    category_index_en = env.ref(
        "alc_app_eshop_b2b.elasticsearch_shopinvader_category_index_en_US"
    )

    for category_index in [category_index_fr, category_index_nl, category_index_en]:
        _logger.info("Migrate shopinvader_category for index %s", category_index.name)
        # create se_binding
        env.cr.execute(
            """
            INSERT INTO se_binding (
                backend_id,
                index_id,
                res_id,
                res_model,
                data,
                state,
                create_date,
                write_date,
                create_uid,
                write_uid,
                active
                )
            SELECT
                %(backend_id)s,
                %(index_id)s,
                shopinvader_category.record_id,
                'product.category',
                to_jsonb(shopinvader_category.data),
                'done',
                shopinvader_category.create_date,
                shopinvader_category.write_date,
                shopinvader_category.create_uid,
                shopinvader_category.write_uid,
                shopinvader_category.active
            FROM
                shopinvader_category
            WHERE
                shopinvader_category.lang_id = %(lang_id)s
            """,
            {
                "backend_id": category_index.backend_id.id,
                "index_id": category_index.id,
                "lang_id": category_index.lang_id.id,
            },
        )
        _logger.info("%d se_binding created", env.cr.rowcount)


@openupgrade.migrate()
def migrate(env, version):
    migrate_shopinvader_variant(env)
    migrate_shopinvader_category(env)
