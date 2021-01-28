# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import api, fields, models


class AbcClassificationProfile(models.Model):

    _inherit = "abc.classification.profile"

    picking_zone_ids = fields.Many2many(
        comodel_name="picking.zone",
        relation="abc_classification_profile_picking_zone_rel",
        column1="profile_id",
        column2="picking_zone_id",
    )

    @api.model
    def create(self, vals):
        res = super(AbcClassificationProfile, self).create(vals)
        if "picking_zone_ids" in vals:
            res._manage_products()
        return res

    def write(self, vals):
        res = super(AbcClassificationProfile, self).write(vals)
        if "picking_zone_ids" in vals:
            self._manage_products()
        return res

    def _unlink_profile_for_zones(self):
        """
        Remove products linked to the profile but with a picking zone not
        into the list of profile's picking zones
        """
        product_profiles_field = self.env["product.product"]._fields[
            "abc_classification_profile_ids"
        ]
        product_profiles_product_col = product_profiles_field.column1
        product_profiles_profile_col = product_profiles_field.column2
        product_profiles_table = product_profiles_field.relation

        template_profiles_field = self.env["product.template"]._fields[
            "abc_classification_profile_ids"
        ]
        template_profiles_product_col = template_profiles_field.column1
        template_profiles_profile_col = template_profiles_field.column2
        template_profiles_table = template_profiles_field.relation
        for rec in self:
            obsolete_products = self.env["product.product"].search(
                [
                    ("picking_zone_id", "not in", rec.picking_zone_ids.ids),
                    ("abc_classification_profile_ids", "in", rec.ids),
                ]
            )
            if not obsolete_products:
                continue
            # remove link on variant
            self.env.cr.execute(
                """
                DELETE FROM %(table)s
                WHERE
                    %(profile_col)s = %(profile_id)s
                    AND %(product_col)s in %(product_ids)s
            """,
                {
                    "table": AsIs(product_profiles_table),
                    "profile_col": AsIs(product_profiles_profile_col),
                    "product_col": AsIs(product_profiles_product_col),
                    "profile_id": rec.id,
                    "product_ids": tuple(obsolete_products.ids),
                },
            )
            # remove link on template
            self.env.cr.execute(
                """
                DELETE FROM %(table)s
                WHERE
                    %(profile_col)s = %(profile_id)s
                    AND %(product_col)s in %(product_ids)s
            """,
                {
                    "table": AsIs(template_profiles_table),
                    "profile_col": AsIs(template_profiles_profile_col),
                    "product_col": AsIs(template_profiles_product_col),
                    "profile_id": rec.id,
                    "product_ids": tuple(
                        obsolete_products.mapped("product_tmpl_id").ids
                    ),
                },
            )

            # remove computed levels
            self.env.cr.execute(
                """
                DELETE FROM %(table)s
                WHERE
                    product_id in %(product_ids)s
                    AND profile_id = %(profile_id)s
                """,
                {
                    "profile_id": rec.id,
                    "product_ids": tuple(obsolete_products.ids),
                    "table": AsIs(self.env["abc.classification.product.level"]._table),
                },
            )

        self.env["product.template"].invalidate_cache(
            ["abc_classification_profile_ids", "abc_classification_product_level_ids"]
        )
        self.env["product.product"].invalidate_cache(
            ["abc_classification_profile_ids", "abc_classification_product_level_ids"]
        )

    def _link_profile_for_zones(self):
        """
        Ensure products with a picking zone into the list of profile's picking zone
        are linked to this profile
        """
        product_profiles_field = self.env["product.product"]._fields[
            "abc_classification_profile_ids"
        ]
        product_profiles_product_col = product_profiles_field.column1
        product_profiles_profile_col = product_profiles_field.column2
        product_profiles_table = product_profiles_field.relation

        template_profiles_field = self.env["product.template"]._fields[
            "abc_classification_profile_ids"
        ]
        template_profiles_product_col = template_profiles_field.column1
        template_profiles_profile_col = template_profiles_field.column2
        template_profiles_table = template_profiles_field.relation

        for rec in self.filtered("picking_zone_ids"):
            self.env.cr.execute(
                """
                INSERT into %(table)s (%(product_col)s, %(profile_col)s)
                SELECT pp.id, %(profile_id)s
                FROM product_product PP
                JOIN product_template pt on pp.product_tmpl_id = pt.id
                WHERE pt.picking_zone_id in %(picking_zone_ids)s
                ON CONFLICT DO NOTHING;
            """,
                {
                    "table": AsIs(product_profiles_table),
                    "product_col": AsIs(product_profiles_product_col),
                    "profile_col": AsIs(product_profiles_profile_col),
                    "profile_id": rec.id,
                    "picking_zone_ids": tuple(rec.picking_zone_ids.ids),
                },
            )
            self.env.cr.execute(
                """
                INSERT into %(table)s (%(product_col)s, %(profile_col)s)
                SELECT pt.id, %(profile_id)s
                FROM  product_template pt
                WHERE pt.picking_zone_id in %(picking_zone_ids)s
                ON CONFLICT DO NOTHING;
            """,
                {
                    "table": AsIs(template_profiles_table),
                    "product_col": AsIs(template_profiles_product_col),
                    "profile_col": AsIs(template_profiles_profile_col),
                    "profile_id": rec.id,
                    "picking_zone_ids": tuple(rec.picking_zone_ids.ids),
                },
            )
        self.env["product.template"].invalidate_cache(
            ["abc_classification_profile_ids"]
        )
        self.env["product.product"].invalidate_cache(["abc_classification_profile_ids"])

    def _manage_products(self):
        """ Manage profile auto assignment to products

        Remove products linked to the profile but with a picking zone not
        into the list of profile's picking zones

        Ensure products with a picking zone into the list of profile's picking zone
        are linked to this profile
        """
        self._unlink_profile_for_zones()
        self._link_profile_for_zones()
