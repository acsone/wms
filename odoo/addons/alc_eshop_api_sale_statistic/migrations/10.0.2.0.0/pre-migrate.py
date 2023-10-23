# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    # the cron xml_id has been changed, we delete it so it can be created anew
    env.ref("alc_eshop_sale_statistic.refresh_materialized_view").unlink()
