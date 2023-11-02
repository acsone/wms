# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def pre_init_hook(cr):
    """This hook is called before the database initialization."""
    # rename xmlid
    openupgrade.rename_xmlids(
        cr,
        [
            (
                "alc_search_engine.elasticsearch_backend",
                "alc_search_engine_backend.elasticsearch_backend",
            )
        ],
    )
    # update res_model for alc_search_engine_backend.elasticsearch_backend
    # in ir.model.data
    openupgrade.logged_query(
        cr,
        """
        UPDATE ir_model_data
        SET model = 'se.backend'
        WHERE module = 'alc_search_engine_backend'
        AND name = 'elasticsearch_backend'
        """,
    )
