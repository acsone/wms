# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from pydantic import BaseModel


class SetDeliveryMethodRequest(
    BaseModel,
    revalidate_instances="always",
    validate_assignment=True,
    extra="forbid",
):
    method_id: int
