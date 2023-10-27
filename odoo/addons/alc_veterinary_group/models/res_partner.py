# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields
from odoo.exceptions import ValidationError

from odoo.addons.base.models.res_partner import Partner

from .veterinary_group import VeterinaryGroup


class ResPartner(Partner):

    veterinary_group_ids = fields.Many2many[VeterinaryGroup](
        relation="res_partner_veterinary_group_rel",
        column1="res_partner_id",
        column2="veterinary_group_id",
        string="Veterinary Group",
    )
    is_alcyonnaire = fields.Boolean(compute="_compute_is_alcyonnaire")
    is_alcyonnaire_under_contract = fields.Boolean(
        compute="_compute_is_alcyonnaire_under_contract"
    )
    date_start_contract_alcyonnaire = fields.Date(
        string="Date start contract", tracking=True
    )
    date_end_contract_alcyonnaire = fields.Date(
        string="Date end contract",
        tracking=True,
        help="If the date end contract is not set, the contract is considered as "
        "indefinite. If the date end contract is set, the contract is considered "
        "as closed the day before the date end contract. IOW if the date end "
        "is set at the same day as the date start, the contract is considered "
        "as without duration.",
    )
    is_date_start_contract_editable = fields.Boolean(
        compute="_compute_is_date_start_contract_editable"
    )
    is_date_end_contract_editable = fields.Boolean(
        compute="_compute_is_date_end_contract_editable"
    )
    is_dates_contract_visible = fields.Boolean(
        compute="_compute_is_dates_contract_visible"
    )

    @api.constrains("date_start_contract_alcyonnaire", "date_end_contract_alcyonnaire")
    def _check_date_contract(self):
        today = fields.Date.today()
        for partner in self:
            if (
                partner.date_start_contract_alcyonnaire
                and partner.date_end_contract_alcyonnaire
            ):
                if (
                    partner.date_start_contract_alcyonnaire
                    > partner.date_end_contract_alcyonnaire
                ):
                    raise ValidationError(
                        _("The start date must be anterior to the end date.")
                    )
            if (
                partner.date_start_contract_alcyonnaire
                and partner.date_start_contract_alcyonnaire > today
            ):
                raise ValidationError(
                    _("The start date must be anterior or equal to today.")
                )
            if (
                partner.date_end_contract_alcyonnaire
                and partner.date_end_contract_alcyonnaire > today
            ):
                raise ValidationError(_("The end date must be anterior at today."))

    @api.depends("veterinary_group_ids")
    def _compute_is_alcyonnaire(self):
        for partner in self:
            groups = partner.veterinary_group_ids.filtered("is_alcyonnaire")
            partner.is_alcyonnaire = bool(groups)

    @api.depends(
        "date_start_contract_alcyonnaire",
        "date_end_contract_alcyonnaire",
        "is_alcyonnaire",
    )
    def _compute_is_alcyonnaire_under_contract(self):
        today = fields.Date.today()
        for partner in self:
            is_alcyonnaire_under_contract = False
            if partner.is_alcyonnaire:
                if partner.date_start_contract_alcyonnaire:
                    if partner.date_start_contract_alcyonnaire <= today and (
                        not partner.date_end_contract_alcyonnaire
                        or partner.date_end_contract_alcyonnaire > today
                    ):
                        is_alcyonnaire_under_contract = True
            partner.is_alcyonnaire_under_contract = is_alcyonnaire_under_contract

    @api.depends("veterinary_group_ids", "veterinary_group_ids.is_alcyonnaire")
    def _compute_is_date_start_contract_editable(self):
        for partner in self:
            partner.is_date_start_contract_editable = partner.is_alcyonnaire

    @api.depends(
        "veterinary_group_ids",
        "veterinary_group_ids.is_alcyonnaire",
        "date_start_contract_alcyonnaire",
    )
    def _compute_is_date_end_contract_editable(self):
        for partner in self:
            partner.is_date_end_contract_editable = (
                partner.is_alcyonnaire and partner.date_start_contract_alcyonnaire
            )

    @api.depends(
        "veterinary_group_ids",
        "veterinary_group_ids.is_alcyonnaire",
        "date_start_contract_alcyonnaire",
    )
    def _compute_is_dates_contract_visible(self):
        for partner in self:
            partner.is_dates_contract_visible = (
                partner.is_alcyonnaire or partner.date_start_contract_alcyonnaire
            )

    def _check_date_end_contract_alcyonnaire(self):
        """This method is called on a list of partners when the partner is.

        removed from a alcyonnaire group. It checks that the end date of the
        contract is set.
        """
        partners_without_date_end = self.filtered(
            lambda p: not p.date_end_contract_alcyonnaire
            and p.date_start_contract_alcyonnaire
        )
        if partners_without_date_end:
            raise ValidationError(
                _(
                    "The end date of the contract must be set before leaving the "
                    "group of alcyonnaire.\nPlease set the end date of the contract "
                    "in the partner form for partners: \n %(names)s.",
                    names="\n".join(partners_without_date_end.mapped("display_name")),
                )
            )

    def _check_write_contract_date_allowed(self, vals):
        for partner in self:
            is_alcyonnaire = vals.get("is_alcyonnaire", partner.is_alcyonnaire)
            if not is_alcyonnaire and "veterinary_group_ids" in vals:
                groups = self.env["veterinary.group"].browse(
                    self._fields["veterinary_group_ids"].convert_to_cache(
                        vals.get("veterinary_group_ids"), partner
                    )
                )
                is_alcyonnaire = any(groups.filtered("is_alcyonnaire"))
            date_start_contract_alcyonnaire = vals.get(
                "date_start_contract_alcyonnaire",
                partner.date_start_contract_alcyonnaire,
            )
            date_end_contract_alcyonnaire = vals.get(
                "date_end_contract_alcyonnaire",
                partner.date_end_contract_alcyonnaire,
            )

            if not is_alcyonnaire and date_start_contract_alcyonnaire:
                raise ValidationError(
                    _("The partner must be Alcyonnaire to have a contract.")
                )
            if not is_alcyonnaire and date_end_contract_alcyonnaire:
                raise ValidationError(
                    _("The partner must be Alcyonnaire to have a contract.")
                )
            if (
                is_alcyonnaire
                and not date_start_contract_alcyonnaire
                and date_end_contract_alcyonnaire
            ):
                raise ValidationError(
                    _("The partner must have a start date to end a contract.")
                )

    def write(self, vals):
        self._check_write_contract_date_allowed(vals)
        if "veterinary_group_ids" in vals:
            partners_alcyonnaire = self.filtered("is_alcyonnaire")
        res = super().write(vals)
        if "veterinary_group_ids" in vals:
            partners_no_more_alcyonnaire = partners_alcyonnaire - self.filtered(
                lambda p: p.is_alcyonnaire
            )
            partners_no_more_alcyonnaire._check_date_end_contract_alcyonnaire()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for vals, rec in zip(vals_list, records, strict=True):
            rec._check_write_contract_date_allowed(vals)
        return records
