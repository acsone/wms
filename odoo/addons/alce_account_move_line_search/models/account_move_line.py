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
