# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import falsy2emptystring


class PharmacyExportMapper(Component):
    _name = "esb.pharmacy.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "res.partner"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "pharmacy")

    direct = [
        (falsy2emptystring("ref"), "Id"),
        (falsy2emptystring("name"), "Name"),
        (falsy2emptystring("zip"), "Postcode"),
        (falsy2emptystring("city"), "City"),
        (falsy2emptystring("phone"), "Telephone"),
        (falsy2emptystring("fax"), "Fax"),
    ]

    @mapping
    def compute_country_id(self, record):
        return {"CountryId": record.country_id.esb_ref or ""}

    @mapping
    def compute_street(self, record):
        street = record.street or ""
        if record.street2:
            street += "\n" + record.street2
        return {"Street": street}

    @mapping
    def compute_email(self, record):
        return {"Email": record.email or ""}


class PharmacyCronExporter(Component):

    _name = "esb.pharmacy.cron.exporter"
    _inherit = "esb.cron.exporter"
    _usage = "record.exporter.cron"
    _apply_on = "res.partner"

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "pharmacy")

    def get_items_domain(self):
        return [("pharmacist_of_ids.active", "=", True)]
