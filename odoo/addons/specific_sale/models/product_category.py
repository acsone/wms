# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import api, models, tools


class ProductCategory(models.Model):
    _inherit = "product.category"

    @api.multi
    def has_for_parent(self, category_id):
        self.ensure_one()
        return self._has_for_parent(self.id, category_id)

    @api.multi
    def has_for_parent_xml_id(self, category_xml_id):
        return self.has_for_parent(self._get_id_for_xmlid(category_xml_id))

    @api.model
    @tools.ormcache("category_xml_id")
    def _get_id_for_xmlid(self, category_xml_id):
        # By default self.env.ref is not cached.... since a lot
        # of category xml_ids are used to validate sale_exception
        # we cache the corresponding id to avoid n so lines * 21 queries into
        # the db to get the id from xml id
        record = self.env.ref(category_xml_id)
        if record._name != self._name:
            raise ValueError(
                "Only category xml_id can be used not %s xml_id" % record._name
            )
        return record.id

    @api.model
    @tools.ormcache("category_id", "parent_category_id")
    def _has_for_parent(self, category_id, parent_category_id):
        """Check if category_id is itself or a parent."""
        if category_id == parent_category_id:
            return True
        category_id = self.browse(category_id).parent_id.id
        if not category_id:
            return False
        return self._has_for_parent(category_id, parent_category_id)

    @api.multi
    def write(self, vals):
        result = super(ProductCategory, self).write(vals)
        if "parent_id" in vals:
            self._has_for_parent.clear_cache(self)
        return result

    @api.multi
    def unlink(self):
        result = super(ProductCategory, self).unlink()
        self._has_for_parent.clear_cache(self)
        self._get_id_for_xmlid.clear_cache(self)
        return result
