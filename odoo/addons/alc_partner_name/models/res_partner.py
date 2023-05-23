# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api
from odoo.osv.expression import get_unaccent_wrapper

from odoo.addons.base.models.res_partner import Partner as BasePartner


class ResPartner(BasePartner):
    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        """
        Process ref as a code: do not apply ilike on ref.

        Return matched ref first.
        """
        res = self._search(
            [
                "|",
                "|",
                ("display_name", operator, name),
                ("email", operator, name),
                ("ref", "=ilike", name),
            ],
            limit=limit,
            access_rights_uid=name_get_uid,
        )
        unaccent = get_unaccent_wrapper(self.env.cr)
        order_name = name
        if operator in ("ilike", "like"):
            order_name = f"%{name}%"
        order_operator = operator
        if operator in ("=ilike", "=like"):
            order_operator = operator[1:]
        res.order = (
            "ref ilike {percent} desc, {display_name} {operator} {percent} desc,"
            " {display_name}".format(
                operator=order_operator,
                display_name=unaccent("display_name"),
                percent=unaccent("%s"),
            )
        )
        res._where_params = res._where_params + [name, order_name]
        return res

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
