# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _confirm_background_sales(env):
    """
    Some sales can be in 'confirm_background' state at migration.

    As the module is not used anymore, confirm them (with orm).
    Before, set them as draft in order to avoid possible filters on state
    """

    query = """
        SELECT id FROM sale_order
            WHERE state = 'confirm_background'
    """
    env.cr.execute(query)
    ids = [i[0] for i in env.cr.fetchall()]

    query = """
        UPDATE sale_order
            SET state = 'draft'
            WHERE state = 'confirm_background'
    """
    env.cr.execute(query)

    # Don't try to send mail
    param = (
        env["ir.config_parameter"]
        .sudo()
        .get_param("sale_mail_internal.send_email", False)
    )
    env["ir.config_parameter"].sudo().set_param("sale_mail_internal.send_email", False)
    env["sale.order"].browse(ids).action_confirm()
    env["ir.config_parameter"].sudo().set_param("sale_mail_internal.send_email", param)


@openupgrade.migrate()
def migrate(env, version):
    _confirm_background_sales(env)
