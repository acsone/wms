# Copyright 2021 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import odoo


def migrate(cr, version):
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    domain = [("name", "ilike", "field%unit_in_shrink_wrap")]
    to_fix = env["ir.model.data"].search(domain)
    to_fix.write({"module": "alc_product_packaging"})
