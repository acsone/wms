# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


def column_exists(cr, tablename, columnname):
    """ Return whether the given column exists. """
    query = """ SELECT 1 FROM information_schema.columns
                WHERE table_name=%s AND column_name=%s """
    cr.execute(query, (tablename, columnname))
    return cr.rowcount


def migrate(cr, version):
    if not version:
        return
    if not column_exists(cr, "sale_order_line", "product_type"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN product_type varchar;
        """
        )
    if not column_exists(cr, "sale_order_line", "is_consignment"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
            ADD COLUMN is_consignment boolean;
        """
        )
    cr.execute(
        """
        UPDATE sale_order_line l
        SET product_type = t.type
        FROM product_product p, product_template t
        WHERE t.id = p.product_tmpl_id
        AND p.id = l.product_id
        AND l.product_type IS NULL;
    """
    )
    cr.execute(
        """
        UPDATE sale_order_line l
        SET is_consignment = o.is_consignment
        FROM sale_order o
        WHERE o.id = l.order_id
        AND l.is_consignment IS NULL;
    """
    )
