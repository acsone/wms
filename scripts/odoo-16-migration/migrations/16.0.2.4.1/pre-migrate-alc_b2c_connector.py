# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _remove_model(cr):
    """Remove model alc.b2c.backend (which is still there after alc_b2c_connector update)."""
    model = "alc.b2c.backend"
    table = openupgrade.get_model2table(model)

    # remove ir_model
    query = f"DELETE FROM ir_model WHERE model='{model}'"
    openupgrade.logged_query(cr, query)

    # remove ir_model_data
    query = (
        f"DELETE FROM ir_model_data " f"WHERE name='model_{table}' AND model='ir.model'"
    )
    openupgrade.logged_query(cr, query)
    query = f"DELETE FROM ir_model_data WHERE model='{model}'"
    openupgrade.logged_query(cr, query)

    # remove ir_attachment
    query = f"DELETE FROM ir_attachment WHERE res_model='{model}'"
    openupgrade.logged_query(cr, query)

    # remove ir_model_fields
    query = f"DELETE FROM ir_model_fields WHERE model='{model}'"
    openupgrade.logged_query(cr, query)
    query = f"DELETE FROM ir_model_fields WHERE relation='{model}'"
    openupgrade.logged_query(cr, query)

    # remove _ir_translation
    query = f"DELETE FROM _ir_translation WHERE name LIKE '{model},%%'"
    openupgrade.logged_query(cr, query)

    # remove ir_filters
    query = f"DELETE FROM ir_filters WHERE model_id='{model}'"
    openupgrade.logged_query(cr, query)

    # remove ir_property
    query = f"DELETE FROM ir_property WHERE res_id LIKE '{model},%%'"
    openupgrade.logged_query(cr, query)
    query = f"DELETE FROM ir_property WHERE value_reference LIKE '{model},%%'"
    openupgrade.logged_query(cr, query)

    # remove ir_exports
    query = f"DELETE FROM ir_exports WHERE resource = '{model}'"
    openupgrade.logged_query(cr, query)

    # remove mail_message
    query = f"DELETE FROM mail_message WHERE model = '{model}'"
    openupgrade.logged_query(cr, query)
    query = f"DELETE FROM mail_message_subtype WHERE res_model = '{model}'"
    openupgrade.logged_query(cr, query)
    query = f"DELETE FROM mail_template WHERE model = '{model}'"
    openupgrade.logged_query(cr, query)

    # remove mail_followers
    query = f"DELETE FROM mail_followers WHERE res_model = '{model}'"
    openupgrade.logged_query(cr, query)

    # remove mail_activity
    query = f"DELETE FROM mail_activity WHERE res_model = '{model}'"
    openupgrade.logged_query(cr, query)

    # drop model table
    query = f"DROP TABLE IF EXISTS {table}"
    openupgrade.logged_query(cr, query)


def migrate(cr, version):
    _remove_model(cr)
