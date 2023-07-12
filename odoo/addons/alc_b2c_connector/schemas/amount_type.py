# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from enum import Enum


class AmountType(Enum):
    fixed = "fixed"
    percent = "percent"
    division = "division"
