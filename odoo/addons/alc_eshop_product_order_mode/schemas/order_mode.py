# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from enum import Enum


class OrderMode(Enum):
    """Enum for product shop order mode."""

    direct_sale_only = "direct_sale_only"
    quotation_only = "quotation_only"
    direct_sale_or_quotation = "direct_sale_or_quotation"
