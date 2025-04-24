# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info(
        "Ensures the field `abc_storage` matches the first element of the field `abc_classification_product_level_ids` on product templates."
    )
    query = """
        WITH first_classification AS (
            SELECT DISTINCT ON (pt.id)
                pt.id AS product_template_id,
                COALESCE(acl.name, 'b') AS classification_name
            FROM
                product_template pt
            LEFT JOIN product_product pp ON pp.product_tmpl_id = pt.id
            LEFT JOIN abc_classification_product_level acpl ON acpl.product_id = pp.id
            LEFT JOIN abc_classification_level acl ON acpl.level_id = acl.id
            ORDER BY pt.id, acpl.id ASC
        )
        UPDATE product_template pt
        SET abc_storage = fc.classification_name
        FROM first_classification fc
        WHERE pt.id = fc.product_template_id;
    """
    cr.execute(query)
