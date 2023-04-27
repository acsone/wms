# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.osv.expression import get_unaccent_wrapper

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Process ref as a code: do not apply ilike on ref.

        Return matched ref first.
        This is a copy/paste of the standard method where only 'ilike %ref%'
        has been changed into '= ref' in the query below.
        """
        if args is None:
            args = []
        if name and operator in ("=", "ilike", "=ilike", "like", "=like"):
            self.check_access_rights("read")
            where_query = self._where_calc(args)
            self._apply_ir_rules(where_query, "read")
            _from_clause, where_clause, where_clause_params = where_query.get_sql()
            where_str = f" WHERE {where_clause if where_clause else ' WHERE '} AND "

            # search on the name of the contacts and of its company
            search_name = name
            if operator in ("ilike", "like"):
                search_name = f"{name}"
            if operator in ("=ilike", "=like"):
                operator = operator[1:]

            unaccent = get_unaccent_wrapper(self.env.cr)

            query = """SELECT id
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
                query += " limit %s"
                where_clause_params.append(limit)
            # pylint: disable=sql-injection
            self.env.cr.execute(query, where_clause_params)
            partner_ids = map(lambda x: x[0], self.env.cr.fetchall())

            if partner_ids:
                return self.browse(partner_ids).name_get()
            return []
        return super().name_search(name, args, operator=operator, limit=limit)

    def name_get(self):
        if self.env.context.get("show_address_only"):
            return super().name_get()
        html_format = self.env.context.get("html_format")
        to_html = html_format or self.env.context.get("to_html")
        nameget = dict(
            super(ResPartner, self.with_context(html_format=False)).name_get()
        )
        res = []
        for partner in self:
            full = []

            self.check_partner_commercial_partner(partner, full)

            name = partner.name or ""
            if name and partner.title:
                title = partner.title.shortcut or partner.title.name
                name = f"{title} {name}"
            elif name and partner.is_company and partner.legal_form_id:
                title = partner.legal_form_id.name
                name = f"{title} {name}"
            full.append(name)

            if partner.suite:
                full.append(partner.suite)

            if to_html and not self.env.context.get("show_email"):
                fullname = "\n".join(full)
            else:
                fullname = ", ".join(full)

            if self.env.context.get("show_email") and partner.email:
                fullname = f"{fullname} <{partner.email}>"

            address = nameget[partner.id].split("\n", 1)
            if len(address) > 1:
                fullname += "\n" + address[1]

            if html_format:
                fullname = fullname.replace("\n", "<br/>")

            res.append((partner.id, fullname))
        return res

    def check_partner_commercial_partner(self, partner, full_name):
        if partner.commercial_partner_id != partner:
            p = partner.commercial_partner_id
            name = p.name
            if name and p.title:
                title = p.title.shortcut or p.title.name
                name = f"{title} {name}"
                full_name.append(name)
            elif name and p.is_company and p.legal_form_id:
                title = p.legal_form_id.name
                name = f"{title} {name}"
                full_name.append(name)
