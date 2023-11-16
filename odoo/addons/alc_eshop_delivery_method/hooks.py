from odoo import api


def post_init_hook(cr, registry):
    """This hook is executed after installing the module."""
    env = api.Environment(cr, 1, {})
    carrier_xmlids = [
        "__setup__.deliver_carrier_by_client",
        "__setup__.deliver_carrier_alcyon",
    ]
    for carrier_xmlid in carrier_xmlids:
        carrier = env.ref(carrier_xmlid, raise_if_not_found=False)
        if carrier:
            carrier.available_in_website = True
