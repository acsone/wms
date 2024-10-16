# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from odoo.addons.alc_cerberus_utils import utils
from odoo.addons.stock.models import stock_picking
from odoo.addons.stock.models.stock_lot import StockLot
from odoo.addons.stock.models.stock_move import StockMove


class Lot(BaseModel):
    name: str
    peremption: date | None

    @classmethod
    def from_stock_lot(
        cls, record: StockLot
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            name=record.name,
            peremption=(
                record.expiration_date.date() if record.expiration_date else None
            ),
        )


class Move(BaseModel):
    remaining_qty: float
    prix_net_htva: float
    state: str
    name: str
    reference: str
    lots: list[Lot] = []
    suite: str
    prix_brut_htva: float
    qty_ordered: float

    @classmethod
    def from_stock_move(
        cls, record: StockMove
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        return cls(
            remaining_qty=record.product_uom_qty - record.quantity_done,
            prix_net_htva=record.sale_line_id.price_reduce_taxexcl,
            state=record.state,
            name=record.name,
            reference=record.product_id.default_code,
            lots=[Lot.from_stock_lot(lot) for lot in record.lot_ids],
            suite=record.suite_name,
            prix_brut_htva=record.sale_line_id.price_unit,
            qty_ordered=record.product_qty,
        )


class Partner(BaseModel):
    city: str | None
    street: str | None
    name: str
    country: str | None


class Picking(BaseModel):
    move_lines: list[Move] = []
    date_done: datetime | None
    date: datetime
    partner: Partner
    id: int
    name: str

    @classmethod
    def from_stock_picking(
        cls, record: stock_picking.Picking
    ) -> self:  # noqa: F821  pylint: disable=undefined-variable
        date_done = None
        if record.date_done:
            date_done = utils.odoo_dt_to_dt_utc(record.date_done)
        partner = Partner(
            city=record.partner_id.city or None,
            street=record.partner_id.street or None,
            name=record.partner_id.name,
            country=record.partner_id.country_id.name or None,
        )
        return cls(
            move_lines=[Move.from_stock_move(move) for move in record.move_ids],
            date_done=date_done,
            date=utils.odoo_dt_to_dt_utc(record.date),
            partner=partner,
            id=record.id,
            name=record.name,
        )


class PickingList(BaseModel):
    data: list[Picking]
    size: int
