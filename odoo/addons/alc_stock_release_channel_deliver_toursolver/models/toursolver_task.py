# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from requests.exceptions import RequestException

from odoo.exceptions import UserError

from odoo.addons.stock_release_channel_shipment_advice_toursolver.models.toursolver_task import (
    ToursolverTask as ToursolverTaskBase,
)

_logger = logging.getLogger(__name__)


class ToursolverTask(ToursolverTaskBase):
    @property
    def _is_auto_process(self) -> bool:
        return self.release_channel_id and self.release_channel_id.state in (
            "delivering",
            "delivering_error",
        )

    def _toursolver_send_request(self):
        self.ensure_one()
        if not self._is_auto_process:
            return super()._toursolver_send_request()
        try:
            return super()._toursolver_send_request()
        except (UserError, RequestException) as error:
            _logger.error(error)
            return self.release_channel_id._toursolver_task_auto_process_notify_error(
                error, self
            )

    def _toursolver_check_status(self):
        self.ensure_one()
        if not self._is_auto_process:
            return super()._toursolver_check_status()
        try:
            res = super()._toursolver_check_status()
            self._release_channel_notify_error(self.toursolver_error_message)
            return res
        except (UserError, RequestException) as error:
            _logger.error(error)
            return self.release_channel_id._toursolver_task_auto_process_notify_error(
                error, self
            )

    def _toursolver_get_result(self):
        self.ensure_one()
        if not self._is_auto_process:
            return super()._toursolver_get_result()
        try:
            res = super()._toursolver_get_result()
            self._release_channel_notify_error(self.toursolver_error_message)
            return res
        except (UserError, RequestException) as error:
            _logger.error(error)
            return self.release_channel_id._toursolver_task_auto_process_notify_error(
                error, self
            )

    def _toursolver_notify_error(self, error_msg):
        res = super()._toursolver_notify_error(error_msg)

        self._release_channel_notify_error(error_msg)
        return res

    def _release_channel_notify_error(self, error_msg):
        if self._is_auto_process and self.state == "error":
            self.release_channel_id._toursolver_task_auto_process_notify_error(
                error_msg, self
            )
