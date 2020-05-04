# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class EdiSynchronizer(AbstractComponent):
    """ Base class for synchronizers """

    _name = "edi.synchronizer"
    _inherit = ["base.synchronizer", "edi.base"]

    @property
    def _base_backend_adapter_usage(self):
        return "{}.backend.adapter".format(self.backend_record.channel)
