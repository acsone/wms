# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models, tools


class Base(models.AbstractModel):

    _inherit = "base"

    @api.model
    @tools.ormcache("category_xml_id")
    def _get_id_for_xmlid(self, category_xml_id, raise_if_not_found=True):
        record = self.env.ref(category_xml_id, raise_if_not_found=raise_if_not_found)
        if record and record._name != self._name:
            msg = _("Expected an id on %s, but the xml_id is on model %s.")
            raise ValueError(msg % (self._name, record._name))
        return record.id if record else False
