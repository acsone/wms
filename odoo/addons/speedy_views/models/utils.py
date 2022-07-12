# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import logging

from psycopg2.extensions import AsIs

_logger = logging.getLogger(__name__)


def create_index(cr, index_name, table, expression):
    cr.execute("SELECT indexname FROM pg_indexes WHERE indexname = %s", (index_name,))
    if not cr.fetchone():
        _logger.info("Create index %s on %s %s", index_name, table, expression)
        cr.execute(
            "CREATE INDEX %s " "ON %s %s",
            (AsIs(index_name), AsIs(table), AsIs(expression)),
        )
