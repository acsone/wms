# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from enum import Enum
from typing import Optional

from odoo.addons.base.models.res_partner import PartnerTitle


class Title(Enum):
    mr = "mr"
    mm = "mm"

    @classmethod
    def from_partner_title(cls, obj: PartnerTitle | None) -> Optional["Title"]:
        if not obj:
            return None
        if obj.name == "Madam":
            return cls.mm
        return cls.mr
