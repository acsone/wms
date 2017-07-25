# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    esb_exported = fields.Boolean()

    @api.multi
    def unlink(self):
        for record in self:
            if self.esb_exported:
                raise exceptions.UserError(
                    _("The customer has already been exported, it can be "
                      "archived  but not deleted."))
            return super(ResPartner, self).unlink()
