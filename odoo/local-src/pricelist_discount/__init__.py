# -*- coding: utf-8 -*-
# © 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from . import models


def force_discount_policy(cr, registry):
    """ Set all pricelist discount_policy at without_discount
    """

    cr.execute(
        "UPDATE product_pricelist set discount_policy ='without_discount'"
    )
