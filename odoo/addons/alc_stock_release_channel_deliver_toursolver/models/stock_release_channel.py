# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, api, fields
from odoo.exceptions import UserError

from odoo.addons.stock_release_channel_shipment_advice_deliver.models.stock_release_channel import (
    StockReleaseChannel as StockReleaseChannelBase,
)


class StockReleaseChannel(StockReleaseChannelBase):

    is_mobile_export_allowed = fields.Boolean(
        compute="_compute_is_mobile_export_allowed"
    )

    def _toursolver_task_auto_process_notify_error(self, error, related_object):
        self.ensure_one()
        if self.state == "delivering_error":
            return
        self.action_delivering_error()
        self.delivering_error = self._get_delivering_error_message(
            error, related_object
        )

    @api.depends("state")
    def _compute_is_mobile_export_allowed(self):
        for rec in self:
            rec.is_mobile_export_allowed = rec.state == "delivered"

    def _check_is_mobile_export_allowed(self):
        for rec in self:
            if not rec.is_mobile_export_allowed:
                raise UserError(
                    _(
                        "Action 'Export to Mobile App' is not allowed for channel "
                        "%(name)s.",
                        name=rec.name,
                    )
                )

    def button_export_to_mobile_app(self):
        """Makes the delivery round available into the mobile APP."""
        return self._delay_export_optimization_to_operational_planning()

    def _delay_export_optimization_to_operational_planning(self):
        """
        Delay the export of the result of an optimization to operational.

        planning
        """
        for record in self:
            self.env.user.notify_info(
                _(
                    "The release channel %(channel)s will be exported to the Mobile "
                    "App into background.",
                    channel=record.display_name,
                )
            )
            description = _(
                "Export optimization result to operational planning for %(channel)s",
                channel=record.display_name,
            )
            record.with_delay(
                description=description
            )._export_optimization_to_operational_planning()

    def _export_optimization_to_operational_planning(self):
        """
        Exports the result of an optimization to operational planning that.

        mobile resources will be able to browse on the field through a mobile
        app.
        This command only works on completed optimizations.
        https://geoservices.geoconcept.com/ToursolverCloud/api-book.html
        #_resource_toursolverwebservice_exporttooperationplanning_post
        """
        self.ensure_one()
        self._check_is_action_print_allowed()
        done_shipment_advices = self.in_process_shipment_advice_ids.filtered(
            lambda s: s.state == "done"
        )
        if not done_shipment_advices:
            raise UserError(
                _(
                    "%(channel)s has nothing to export to Mobile App",
                    channel=self.display_name,
                )
            )
        for sa in done_shipment_advices:
            task = sa.toursolver_task_id
            if task.state not in ("success", "done"):
                error_message = _(
                    "Can't export a not complete optimization for "
                    "%(shipment_advice)s",
                    shipment_advice=sa.display_name,
                )
                raise UserError(error_message)
            action = "exportToOperationalPlanning"
            json_request = sa._generate_optimization_operational_export_request()
            result = task._toursolver_post(action, json_request)
            if not result:
                return False
            self.env.user.notify_info(
                _(
                    "Optimization for %(channel)s exported to operational planning.",
                    channel=self.display_name,
                )
            )
        return json_request
