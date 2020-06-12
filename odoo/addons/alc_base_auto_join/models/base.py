# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo import api, models


class Base(models.AbstractModel):

    _inherit = "base"

    @contextmanager
    @api.model
    def _auto_join(self, field_names):
        """
        Force auto_join on the provided fields. The initial value defined on
        fields is restored at the end of the call.

        When the left side of a domain leaf contains a dot ie
        "order_line.qty_to_invoice", the orm will first query the
        linked model (select id from sale_order_line where qty_to_invoice...)
        and use the result into the query on the initial model with a in
        operator. This process could lead to huge and inefficient queries
        By using auto_join, we temporarily instruct the ORM that a SQL
        join can be safely be used when building the SQL query in place
        of the dummy mechanism. This is only safe if we are sure that no
        record rule applies to the linked model
        """
        initial_values = {}
        try:
            for fn in field_names:
                field = self._fields[fn]
                initial_values[field] = field.auto_join
                field.auto_join = True
            yield
        finally:
            for field, value in initial_values.items():
                field.auto_join = value
