# -*- coding: utf-8 -*-
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv.expression import get_unaccent_wrapper


class ResPartner(models.Model):
    _inherit = "res.partner"

    alcyon_category_id = fields.Many2one(
        "partner.alcyon_category", string="Alcyon category"
    )
    ref = fields.Char(copy=False, readonly=True)

    vet_depot_number = fields.Char(string="Depot number")
    vet_subscription_number = fields.Char(string="Subscription number")

    is_veterinary = fields.Boolean(compute="_compute_is_veterinary_or_students")
    is_students = fields.Boolean(compute="_compute_is_veterinary_or_students")

    legal_entity_id = fields.Many2one("legal.entity", string="Legal entity")

    pharmacist_id = fields.Many2one(
        comodel_name="res.partner", string="Associated pharmacist"
    )
    pharmacist_of_ids = fields.One2many(
        comodel_name="res.partner",
        inverse_name="pharmacist_id",
        string="Pharmacist associated to",
    )

    master_partner_id = fields.Many2one(
        comodel_name="res.partner", string="Customer master"
    )

    # temporary field to get the data and make it
    # possible to create contacts by hand in Odoo
    suite = fields.Char("Suite Name")
    call_name = fields.Char(string="Nickname")

    apb_authorization = fields.Char(string="Authorization/APB")

    @api.depends("alcyon_category_id")
    def _compute_is_veterinary_or_students(self):
        veterinary = self.env.ref("specific_partner.partner_category_veterinary")
        students = self.env.ref("specific_partner.partner_category_student")
        for partner in self:
            partner.is_veterinary = partner.alcyon_category_id == veterinary
            partner.is_students = partner.alcyon_category_id == students

    @api.model
    def _commercial_fields(self):
        """Cancel propagation of the field ref to children.

        This changes the default behavior of the module base_partner_sequence,
         """
        res = super(ResPartner, self)._commercial_fields()
        if "ref" in res:
            res.remove("ref")
        return res

    @api.multi
    def _needsRef(self, vals=None):
        """Generate a unique ref for addresses and contacts.

        This changes the default behavior of the module base_partner_sequence.
        """
        res = super(ResPartner, self)._needsRef(vals)
        if vals and vals.get("parent_id"):
            return True
        return res

    type_delivery = fields.Boolean(
        "Is Also Delivery",
        help="Allow to mark an invoice address as also a delivery address",
    )
    type_name = fields.Char("Address Type Name", compute="_compute_type_name")

    @api.multi
    def _compute_type_name(self):
        for partner in self:
            name = False
            if partner.type == "invoice" and partner.type_delivery:
                name = _("Invoice and delivery")
            elif partner.type:
                name = dict(self.fields_get(["type"])["type"]["selection"])[
                    partner.type
                ]
            partner.type_name = name

    @api.multi
    def address_get(self, adr_pref=None):
        """ Copy of default method. Changes:
        * Do not use the 'contact' partner as a default address, return self
            In standard, if an address for a given type is not found, any
            contact is returned instead of current partner
        * Check field type_delivery
            Allow an address to be both invoice and delivery. As in standard,
            the search is performed on children and then on children of the
            commercial entity, we do not want to catch a delivery address of
            another child of the commercial entity
        """
        adr_pref = set(adr_pref or [])
        result = {}
        visited = set()
        for partner in self:
            current_partner = partner
            while current_partner:
                to_scan = [current_partner]
                # Scan descendants, DFS
                while to_scan:
                    record = to_scan.pop(0)
                    visited.add(record)
                    # jbaudoux: add 'invoice and delivery' in search
                    rtypes = [record.type]
                    if rtypes == ["invoice"] and record.type_delivery:
                        rtypes = ["invoice", "delivery"]
                    for rtype in rtypes:
                        if rtype in adr_pref and not result.get(rtype):
                            result[rtype] = record.id
                        if len(result) == len(adr_pref):
                            return result
                    # jbaudoux: end of change
                    to_scan = [
                        c
                        for c in record.child_ids
                        if c not in visited
                        if not c.is_company
                    ] + to_scan

                # Continue scanning at ancestor if current_partner is not a
                # commercial entity
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id

        # jbaudoux: remove partner of type 'contact' as default, use self
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or self.id
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Process ref as a code: do not apply ilike on ref.
        Return matched ref first.
        This is a copy/paste of the standard method where only 'ilike %ref%'
        has been changed into '= ref' in the query below."""
        if args is None:
            args = []
        if name and operator in ("=", "ilike", "=ilike", "like", "=like"):
            self.check_access_rights("read")
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, "read")
            from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = where_clause and (" WHERE %s AND " % where_clause) or " WHERE "

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ("ilike", "like"):
                search_name = "%%%s%%" % name
            if operator in ("=ilike", "=like"):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = u"""SELECT id
                         FROM res_partner
                      {where} ({email} {operator} {percent}
                           OR {display_name} {operator} {percent}
                           OR ref = {percent})
                           -- don't panic, trust postgres bitmap
                     ORDER BY ref = {percent} desc,
                              {display_name} {operator} {percent} desc,
                              {display_name}
                    """.format(
                where=where_str,
                operator=operator,
                email=unaccent("email"),
                display_name=unaccent("display_name"),
                percent=unaccent("%s"),
            )

            where_clause_params += [search_name] * 2 + [name] * 2 + [search_name]
            if limit:
                query += u" limit %s"
                where_clause_params.append(limit)
            self.env.cr.execute(query, where_clause_params)  # pylint: disable=E8103
            partner_ids = map(lambda x: x[0], self.env.cr.fetchall())

            if partner_ids:
                return self.browse(partner_ids).name_get()
            else:
                return []
        return super(ResPartner, self).name_search(
            name, args, operator=operator, limit=limit
        )

    @api.multi
    def name_get(self):
        if self.env.context.get("show_address_only"):
            return super(ResPartner, self).name_get()
        html_format = self.env.context.get("html_format")
        to_html = html_format or self.env.context.get("to_html")
        nameget = dict(
            super(ResPartner, self.with_context(html_format=False)).name_get()
        )
        res = []
        for partner in self:
            full = []

            if partner.commercial_partner_id != partner:
                p = partner.commercial_partner_id
                name = p.name
                if name and p.title:
                    title = p.title.shortcut or p.title.name
                    name = u"{} {}".format(title, name)
                    full.append(name)
                elif name and p.is_company and p.legal_entity_id:
                    title = p.legal_entity_id.name
                    name = u"{} {}".format(title, name)
                    full.append(name)

            name = partner.name or ""
            if name and partner.title:
                title = partner.title.shortcut or partner.title.name
                name = u"{} {}".format(title, name)
            elif name and partner.is_company and partner.legal_entity_id:
                title = partner.legal_entity_id.name
                name = u"{} {}".format(title, name)
            full.append(name)

            if partner.suite:
                full.append(partner.suite)

            if to_html and not self.env.context.get("show_email"):
                fullname = u"\n".join(full)
            else:
                fullname = u", ".join(full)

            if self.env.context.get("show_email") and partner.email:
                fullname = u"{} <{}>".format(fullname, partner.email)

            address = nameget[partner.id].split(u"\n", 1)
            if len(address) > 1:
                fullname += u"\n" + address[1]

            if html_format:
                fullname = fullname.replace(u"\n", u"<br/>")

            res.append((partner.id, fullname))
        return res

    @api.multi
    def message_subscribe(
        self, partner_ids=None, channel_ids=None, subtype_ids=None, force=True
    ):
        """
        Add subtype to note automatically for partner
        """
        # Get the id from "Note"
        subtype_note_xmlids = "mail.mt_note"
        subtype_note_id = self.env["ir.model.data"].xmlid_to_res_id(subtype_note_xmlids)
        # Get default subtype item for partner
        partner_default_subtype_ids = (
            self.env["mail.message.subtype"]
            .search(
                [
                    "|",
                    ("res_model", "=", False),
                    "&",
                    ("res_model", "=", "res.partner"),
                    ("default", "=", True),
                ]
            )
            .ids
        )
        # add "note id" to be selected
        if subtype_ids:
            subtype_ids += partner_default_subtype_ids
        else:
            subtype_ids = partner_default_subtype_ids
        if subtype_note_id and subtype_note_id not in subtype_ids:
            subtype_ids.append(subtype_note_id)
        return super(ResPartner, self).message_subscribe(
            partner_ids=partner_ids,
            channel_ids=channel_ids,
            subtype_ids=subtype_ids,
            force=force,
        )

    @api.constrains("name", "street", "city", "zip", "country_id")
    def _is_valid_esb_address(self):
        """Check customer address validity.

        Invoicing and delivery address of customer are sent to the esb,
        and some fields are required for them to be valid.
        And check is made in the view as well.
        """
        for rec in self:
            if not rec.parent_id or not rec.customer:
                return
            if rec.type not in ["invoice", "delivery"]:
                return
            if (
                rec.name
                and rec.street
                and rec.city
                and rec.zip
                and rec.country_id.esb_ref
            ):
                return
            raise ValidationError(
                _(
                    "For an invoicing or delivery address the "
                    "following fields (name, street, city, zip, "
                    "country) are required. And the country "
                    "must have a reference ESB."
                )
            )
