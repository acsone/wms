# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from enum import Enum
from typing import Any


class Title(Enum):
    mr = "mr"
    mm = "mm"

    @classmethod
    def from_orm(cls: Enum, obj: Any) -> str:
        if not obj:
            return None
        if obj.name == "Madam":
            return "mm"
        return "mr"
