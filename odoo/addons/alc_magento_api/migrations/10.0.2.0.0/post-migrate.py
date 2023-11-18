# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    cr.execute(
        "update ir_module_module set state = 'to remove' "
        "where name ='elasticsearch_product_cache'"
    )
