from odoo import SUPERUSER_ID, api


def migrate(cr, version=None):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("alc_app_eshop_b2b.large").write({"size_x": 550, "size_y": 550})
