# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)


from odoo import _, api, exceptions, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    esb_exported = fields.Boolean(copy=False)

    @api.multi
    def write(self, vals):
        if "default_code" in vals:
            new_code = vals["default_code"]
            for record in self:
                if record.esb_exported and record.default_code != new_code:
                    raise exceptions.UserError(
                        _(
                            "Reference can't be modified once a product "
                            "has been exported."
                        )
                    )
        return super(ProductProduct, self).write(vals)

    def unlink(self):
        for record in self:
            if record.esb_exported:
                raise exceptions.UserError(
                    _(
                        "The client has already been exported, "
                        "it can be archived but not deleted."
                    )
                )
        return super(ProductProduct, self).unlink()


class ProductTemplate(models.Model):
    _inherit = "product.template"

    esb_exported = fields.Boolean(compute="_compute_esb_exported", store=True)

    @api.depends("product_variant_ids", "product_variant_ids.esb_exported")
    def _compute_esb_exported(self):
        for template in self:
            template.esb_exported = any(
                variant.esb_exported for variant in template.product_variant_ids
            )
