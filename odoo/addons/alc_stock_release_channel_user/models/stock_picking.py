# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api
from odoo.exceptions import ValidationError

from odoo.addons.stock_release_channel.models.stock_picking import (
    StockPicking as StockPickingBase,
)


class StockPicking(StockPickingBase):
    def _should_check_user(self):
        self.ensure_one()
        return (
            self.state not in ("done", "cancel")
            and self.release_channel_id.user_ids
            and self.user_id
        )

    @api.constrains("user_id", "release_channel_id")
    def _check_allowed_user(self):
        """Check user is allowed.

        If a release channel is linked to the picking and a list of
        allowed users is defined on it, the user must be into this list.
        """
        for rec in self:
            if not rec._should_check_user():
                continue
            if rec.user_id not in rec.release_channel_id.user_ids:
                raise ValidationError(
                    _(
                        "User {user_name} is not into the list of allowed "
                        "users for the release channel {channel_name} "
                        "({allowed_user_names})."
                    ).format(
                        user_name=rec.user_id.name,
                        channel_name=rec.release_channel_id.display_name,
                        allowed_user_names=" ,".join(
                            rec.release_channel_id.mapped("user_ids.display_name")
                        ),
                    )
                )
