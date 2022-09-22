# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    query = "ALTER TABLE product_template ADD COLUMN number_labels_to_print INTEGER"
    cr.execute(query)
    query_migrate = """
UPDATE product_template
SET number_labels_to_print = CASE
    WHEN "is_do_not_print_label" = true THEN 0
    ELSE 1
END;
"""
    cr.execute(query_migrate)

    query_delete_view = """
DELETE FROM ir_ui_view WHERE id in (
   SELECT res_id
   FROM ir_model_data
   WHERE
       module='specific_print'
       AND model='ir.ui.view'
       AND name='view_template_property_form'
);
"""
    cr.execute(query_delete_view)
