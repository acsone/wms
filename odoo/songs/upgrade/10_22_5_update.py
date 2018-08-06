# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import anthem


@anthem.log
def fix_discount_pricelist_id_partner(ctx):
    """Copy values from property as field was changed to a normal field.

    discount_pricelist_id was a property on respartner. We are changing it
    back to a normal field. So we need to copy values from properties to the
    partner model"""
    properties = ctx.env["ir.property"].search([
        ("name", "=", "discount_pricelist_id"),
        ("res_id", "like", "res.partner,%"),
    ])
    ctx.log_line(
        "Found {} properties to move and delete".format(
            len(properties)
        ),
    )
    for record in properties:
        partner_id = int(record.res_id.split(',')[-1].strip())
        pricelist_id = int(record.value_reference.split(',')[-1].strip())
        # I use direct SQL to prevent check of VAT on the partner
        # as, for some reason, we have partners with incorrect VAT set on them
        ctx.env.cr.execute("""
        UPDATE res_partner
        SET
        discount_pricelist_id=%(pricelist_id)s
        WHERE
        id=%(partner_id)s
        """, {
            "pricelist_id": pricelist_id,
            "partner_id": partner_id
        })
    ctx.log_line("Deleting properties")
    properties.unlink()


@anthem.log
def main(ctx):
    fix_discount_pricelist_id_partner(ctx)
