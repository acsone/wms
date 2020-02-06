# -*- coding: utf-8 -*-
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models, tools


class PartnerAlcyonCategorie(models.Model):
    _name = 'partner.alcyon_category'

    name = fields.Char(string='Name', required=True)
    esb_ref = fields.Char(string='Reference for ESB', required=True)
    _sql_constraints = [
        (
            'name_unique',
            'unique(name)',
            _('This category name already exists'),
        ),
        (
            'esb_ref_unique',
            'unique(esb_ref)',
            _('This reference esb already exists'),
        ),
    ]

    @api.multi
    def is_xml_id(self, xml_id):
        self.ensure_one()
        return self.id == self._get_id_for_xmlid(xml_id)

    @api.model
    @tools.ormcache("xml_id")
    def _get_id_for_xmlid(self, xml_id):
        # By default self.env.ref is not cached.... since a lot
        # of category xml_ids are used to validate sale_exception
        # we cache the corresponding id to avoid n so lines * 12 queries into
        # the db to get the id from xml id
        record = self.env.ref(xml_id)
        if record._name != self._name:
            raise Exception(
                "Only alcyon partner category xml_id can be used not %s xml_id"
                % record._name
            )
        return record.id

    @api.multi
    def unlink(self):
        result = super(PartnerAlcyonCategorie, self).unlink()
        self._get_id_for_xmlid.clear_cache(self)
        return result
