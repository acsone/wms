# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        """
        UPDATE product_product as pp
        SET
            manufacturer_id = pt.manufacturer_id,
            manufacturer_pname = pt.manufacturer_pname,
            manufacturer_pref = pt.manufacturer_pref,
            manufacturer_purl = pt.manufacturer_purl
        FROM product_template AS pt
        WHERE
            (pt.manufacturer_id IS NOT NULL
            OR pt.manufacturer_pname != ''
            OR pt.manufacturer_pref != ''
            OR pt.manufacturer_purl != '')
            AND pt.id = pp.product_tmpl_id
            """
    )
