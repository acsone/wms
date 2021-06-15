# -*- coding: utf-8 -*-
# Copyright 2021 Acsone
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class RoundInstanceCustomer(models.Model):
    _name = "round.instance.customer"
    _inherit = ["delivery.gls.mixin", "round.instance.customer"]

    def _deliver(self, background=True):
        """This override prevents delivery if some GLS package has not been sent yet."""
        self._raise_if_not_sent()
        return super(RoundInstanceCustomer, self)._deliver(background)
