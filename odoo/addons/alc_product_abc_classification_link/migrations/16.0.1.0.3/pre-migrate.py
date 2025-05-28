# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Update `product_product.abc_storage` to match the first element of the field `abc_classification_product_level_ids`."
    )
    product_variants_query = """
        WITH product_variant_calculated_abc AS (
            SELECT
                pp.id AS product_id,
                pp.product_tmpl_id AS template_id,
                COALESCE(acl.name, 'b') AS calculated_abc_storage
            FROM
                product_product pp
            LEFT JOIN LATERAL (
                SELECT acpl_sub.level_id
                FROM abc_classification_product_level acpl_sub
                WHERE acpl_sub.product_id = pp.id
                ORDER BY acpl_sub.id ASC
                LIMIT 1
            ) AS first_acpl ON TRUE
            LEFT JOIN abc_classification_level acl ON first_acpl.level_id = acl.id
        )
        UPDATE product_product pp
        SET abc_storage = pvc.calculated_abc_storage
        FROM product_variant_calculated_abc pvc
        WHERE pp.id = pvc.product_id;
    """
    cr.execute(product_variants_query)

    _logger.info(
        "Update `product_template.abc_storage` to be consistent with the variants."
    )
    product_templates_query = """
        WITH template_final_abc_storage AS (
            SELECT
                pt.id AS template_id,
                CASE
                    WHEN COUNT(DISTINCT pp.abc_storage) = 1 THEN
                        MAX(pp.abc_storage)
                    ELSE
                        'b'
                END AS final_abc_storage
            FROM
                product_template pt
            LEFT JOIN
                product_product pp ON pp.product_tmpl_id = pt.id
            GROUP BY
                pt.id
        )
        UPDATE product_template pt
        SET abc_storage = tfas.final_abc_storage
        FROM template_final_abc_storage tfas
        WHERE pt.id = tfas.template_id;
    """
    cr.execute(product_templates_query)
