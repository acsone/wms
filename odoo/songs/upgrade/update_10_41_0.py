# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import anthem


@anthem.log
def remove_uneeded_delivery_method(ctx):
    """Removing unused delivery carrier.

    This record was added a few month back, it has an xmlid but because it has
    been changed manually in production (to fix a problem) it can not be used
    here.
    """
    delivery_carrier = ctx.env['delivery.carrier'].browse(13)
    if delivery_carrier.exists():
        if delivery_carrier.name == 'Frais de livraison':
            ctx.log_line("Deleting the delivery_carrier id 13.")
            product_id = delivery_carrier.product_id
            delivery_carrier.unlink()
            product_id.product_tmpl_id.unlink()
        else:
            ctx.log_line(
                "The delivery_carrier {} was found but does not "
                " have the correct name !".format(delivery_carrier.name)
            )
    else:
        ctx.log_line("The delivery_carrier to delete was not found !")


@anthem.log
def post(ctx):
    remove_uneeded_delivery_method(ctx)
