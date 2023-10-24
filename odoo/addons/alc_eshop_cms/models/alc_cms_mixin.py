# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import models


class AlcCmsMixin(models.AbstractModel):
    """This mixin should be the root of other CMS mixins,.

    to make sure they have a common root.
    """

    _name = "alc.cms.mixin"
    _description = "CMS Mixin"
