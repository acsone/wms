# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import re
import anthem
from anthem.lyrics.records import add_xmlid


@anthem.log
def standardize_user_xml_ids(ctx):
    """
    Users are directly created in Odoo with the interface.
    However these users don't have a XML ID or some uses have a
    generated XML ID.
    The idea of this method is to standardize created users XML ID.
    """
    base_user_xml_id = "res_user_"
    default_xml_id_regex = r'.*_\d+$'

    get_xml_id_query = \
        "SELECT id, module, name " \
        "FROM ir_model_data " \
        "WHERE model = 'res.users' AND res_id = %s"

    update_xml_id_query = \
        "UPDATE ir_model_data " \
        "SET name = %s, module = '__setup__' WHERE id = %s"

    users = ctx.env['res.users'].search(
        ['|', ('active', '=', True), ('active', '=', False)])
    for user in users:
        ctx.env.cr.execute(get_xml_id_query, (user.id, ))
        result = ctx.env.cr.fetchone()

        if not result:
            user_xml_id = "__setup__.res_user_%s" % user.login
            add_xmlid(ctx, user, user_xml_id)
            continue

        id, module, name = result
        if re.match(default_xml_id_regex, name) \
                and module in ('__setup__', '__export__'):
            user_xml_id = base_user_xml_id + user.login
            ctx.env.cr.execute(update_xml_id_query, (user_xml_id, id))


@anthem.log
def post(ctx):
    """ POST 10.27.5 """
    standardize_user_xml_ids(ctx)
