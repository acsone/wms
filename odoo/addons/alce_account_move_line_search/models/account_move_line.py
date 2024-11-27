# Copyright 2024 ACSONE SA/NV

from odoo import api, fields

from odoo.addons.account.models.account_account import AccountRoot
from odoo.addons.account.models.account_move_line import (
    AccountMoveLine as AccountMoveLineBase,
)


class AccountMoveLine(AccountMoveLineBase):

    name = fields.Char(index="trigram", unaccent=False)
    ref = fields.Char(index="trigram", unaccent=False)
    account_root_id = fields.Many2one[AccountRoot](index="btree")
    account_root_parent_id = fields.Many2one[AccountRoot](
        index="btree", related="account_root_id.parent_id", store=True
    )

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        count=False,
        access_rights_uid=None,
    ):
        """
        'child_of' operator is replaced by in ids, which is not efficient for searching.

        in large datasets.
        To optimize, we intercept the domain and check if there is a leaf on 'account_root_id'.
        If the search targets a child, we replace the 'child_of' operator with '='.
        If the search targets a parent, we replace the search field with a dedicated
        field created specifically for this purpose.
        """
        for leaf in args:
            if not isinstance(leaf, list):
                continue
            if leaf[0] == "account_root_id" and leaf[1] == "child_of":
                account_root_id = leaf[2]
                account_root = self.env["account.root"].browse(account_root_id)
                if not account_root.parent_id:
                    leaf[0] = "account_root_parent_id"
                leaf[1] = "="
        return super()._search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count,
            access_rights_uid=access_rights_uid,
        )

    def _search_panel_domain_image(
        self, field_name, domain, set_count=False, limit=False
    ):
        """
        FIXME: disable account root filter on account move lines.

        When any filter or search is applied, the widget attempts to dynamically filter
        and display only the root accounts that are linked to the search results.
        This filtering process slows down the search, especially when dealing with a
        large dataset or complex queries.

        A ticket has been opened with Odoo #4364037.

        In the meantime, we disable this filter and always display all root accounts.
        This means that, regardless of the search performed, the user will see all root
        accounts, even if no results are found for some of them.

        This approach would provide a significant performance improvement.
        """
        return {
            root.id: {"id": root.id, "display_name": root.display_name}
            for root in self.env["account.root"].search([])
        }
