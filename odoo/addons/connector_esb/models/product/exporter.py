# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo.osv.expression import OR

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping

from ...components.mapper import (
    dt2esbdate,
    falsy2emptystring,
    falsy2zero,
    three_digits_fractional,
    two_digits_fractional,
)


class ProductExportMapper(Component):
    _name = "esb.product.mapper"
    _inherit = ["esb.export.mapper"]
    _apply_on = "product.product"

    direct = [
        ("name", "Gesdem"),
        (falsy2emptystring("default_code"), "Gesart"),
        (falsy2emptystring("barcode"), "Cplz05"),
        (three_digits_fractional("weight"), "Gespnt"),
        (dt2esbdate("create_date"), "Gescrt"),
        (falsy2emptystring("cnk_code"), "Cplz03"),
        (two_digits_fractional("height"), "Cp2z01"),
        (two_digits_fractional("length"), "Cp2z03"),
        (two_digits_fractional("width"), "Cp2z05"),
        (falsy2zero("unit_in_shrink_wrap"), "Cp2z02"),
        (falsy2zero("ratio_main_product"), "Cp2z23"),
        (falsy2zero("ratio_additional_product"), "Cp2z24"),
    ]

    translatable_keys = {"nl_BE": {"name": "Refdem"}}

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "product")

    @mapping
    def pusblished_on_internet(self, record):
        """Mapping for Cplz19

        This defines if the product will apear on Magento
        """
        return {"Cplz19": 1 if record.active and record.web_published else 0}

    @mapping
    def volume(self, record):
        """Mapping for the volume.

        The volume in Odoo is recorded in liter and the ESB expects
        a value in cm3. So convertion is required.
        """
        return {"Cp2z08": "{:.2f}".format((record.volume or 0) * 1000)}

    @mapping
    def supplier(self, record):
        supplier_product_code = ""
        supplier_ref = "0"
        suppliers = record.seller_ids
        if suppliers:
            supplier = suppliers[0]
            supplier_product_code = supplier.product_code or ""
            supplier_ref = supplier.name.ref or "0"

        return {"Gesarc": supplier_product_code, "Gesfou": supplier_ref}

    @mapping
    def manufacturer(self, record):
        manufacturer_ref = "0"
        if record.manufacturer:
            manufacturer_ref = record.manufacturer.ref or "0"
        return {"Cplz25": manufacturer_ref}

    @mapping
    def category_warnings(self, record):
        cat = record.categ_id
        return {
            "Warceg": (cat.with_context({"lang": "de_DE"}).warning_info or "")[:254],
            "Warcfr": (cat.with_context({"lang": "fr_BE"}).warning_info or "")[:254],
            "Warcnl": (cat.with_context({"lang": "nl_BE"}).warning_info or "")[:254],
        }

    @mapping
    def storage_temperature(self, record):
        return {"Cp2z17": record.storage_temperature_id.esb_ref or 0}

    @mapping
    def fixed_fields(self, record):
        """ return hardcoded values for fields """
        zero = ("Cp2z19",)
        values = {f: 0 for f in zero}
        return values

    @mapping
    def temporary_fixed_field(self, record):
        """ This is to help testing before resolution of ALCN-1456."""
        return {"Gescov": 0}

    @mapping
    def measurement_unit_fields(self, record):
        """Fixed fields required by the ESB."""
        return {
            "poids_net-unit": "KILOGRAM",
            "volume-unit": "CUBIC_CENTIMETER",
            "hauteur-unit": "CENTIMETER",
            "longueur-unit": "CENTIMETER",
            "largeur-unit": "CENTIMETER",
        }

    @mapping
    def group_and_subgroup(self, record):
        """The group and sub group of the product.

        The sub group is the group in which the product is.
        The group is the parent group of the sub group

        The group was never imported into Odoo from db2 (product categories
        were revamped with tree structure) so it can not be calculated.

        """
        grp_ref = "0"
        subgrp_ref = record.categ_id.esb_ref or "0"
        # Human products
        if subgrp_ref == "15":
            grp_ref = "6"
        # Cascade products
        if subgrp_ref == "75":
            grp_ref = "75"
        # Stupefiant
        if subgrp_ref == "31":
            grp_ref = "7"
        # Psychotrop annexe III
        if subgrp_ref == "30":
            grp_ref = "1"
        return {
            "Gescgr": grp_ref if grp_ref.isdigit() else "0",
            "Gescsg": subgrp_ref if subgrp_ref.isdigit() else "0",
        }

    @mapping
    def business_unit(self, record):
        unit_ref = ""
        category = record.categ_id
        while category:
            if category.is_business_unit:
                unit_ref = category.esb_ref
                break
            category = category.parent_id
        return {"Cplz14": unit_ref or ""}

    @mapping
    def taxes(self, record):
        ref = ""
        contrib_sku = ""
        for tax in record.taxes_id:
            if tax.esb_ref and not ref:
                ref = tax.esb_ref  # first found
            if tax.contrib_sku and not contrib_sku:
                contrib_sku = tax.contrib_sku  # first found
        return {"Gesctv": ref, "Cplz07": contrib_sku}

    @mapping
    def lot_tracking(self, record):
        return {"Gescsa": 1 if record.tracking != "none" else 0}

    @mapping
    def stockable(self, record):
        """Code de gestion

        This rule has been inverted after the go-live to fix some message
        on Magento.
        """
        return {"Gescge": 0 if record.type == "product" else 1}

    @mapping
    def price_categs(self, record):
        categs = ("GMA", "ALI", "ALG", "ALH", "IMP")
        values = dict.fromkeys(categs, False)
        categ = record.price_category_id.name
        if categ:
            values[categ] = True
        return values

    @mapping
    def uom(self, record):
        return {"Gesunv": record.uom_id.esb_ref or ""}

    @mapping
    def mto(self, record):
        mto_route_id = self.env.ref("stock.route_warehouse0_mto").id
        is_mto = 1 if mto_route_id in record.route_ids.ids else 0
        return {"Gescde": is_mto}

    @mapping
    def product_given(self, record):
        return {"Cp2z22": record.additional_product_id.default_code or ""}


class ProductCronExporter(Component):

    _name = "esb.product.cron.exporter"
    _inherit = ["esb.cron.exporter"]
    _usage = "record.exporter.cron"
    _apply_on = "product.product"

    _mark_as_exported = True

    @classmethod
    def _component_match(cls, work):
        return bool(work.timestamp and work.timestamp.kind == "product")

    def get_items_domain(self):
        """All products are exported to the ESB.

        Except the contrib antibiotic, which were used as a tax on the old
        system (AS/400)
        """
        domain = [
            # Not GESTART.startwith(‘8888’) (contrib antibio)
            ("default_code", "not like", "8888%")
        ]
        return domain

    def get_domain_timestamp_product_tmpl(self, export_since, export_to=None):
        """Domain timestamp for product.template.

        Depending of the fields changed the write_date in the database
        is changed either on the product_product model or product_template.
        """
        domain = [("product_tmpl_id.write_date", ">=", export_since)]
        if export_to:
            domain.append(("product_tmpl_id.write_date", "<=", export_to))
        return domain

    def domain_timestamp(self, export_since=None, export_to=None):
        """Add a check on product_template write_date."""
        return OR(
            [
                super(ProductCronExporter, self).domain_timestamp(
                    export_since, export_to=export_to
                ),
                self.get_domain_timestamp_product_tmpl(
                    export_since, export_to=export_to
                ),
            ]
        )

    def _write_esb_exported_mark_on_records(self, records):
        _super = super(ProductCronExporter, self)
        _super._write_esb_exported_mark_on_records(records)
        # product_template.esb_exported is a computed field based on
        # product_product.esb_exported, but as we bypass the ORM to
        # write in product_product, the computation won't be triggered
        # do the same here. (it bypasses the ORM to avoid to update the
        # write_date which would trigger a new update)
        templates = records.mapped("product_tmpl_id")
        query = "UPDATE %s SET esb_exported = true WHERE id IN %s "
        self.env.cr.execute(query, (AsIs(templates._table), tuple(templates.ids),))
        self.model.invalidate_cache(fnames=["esb_exported"], ids=templates.ids)
        return _super
