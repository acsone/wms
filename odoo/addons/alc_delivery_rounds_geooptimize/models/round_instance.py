# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import json
import logging
import math
import urllib
import urlparse
from datetime import datetime, timedelta

import requests

from odoo import _, api, fields, models
from odoo.addons.queue_job.job import job
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


def seconds_to_duration(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%02d" % (h, m, s)


class RoundInstance(models.Model):

    _inherit = "round.instance"

    geo_optimization_task_id = fields.Char(
        "Optimization task id",
        help="Identifier of the task submitted to the TourSolver service to "
        "optimize the planning/path of the delivery round.",
        readonly=True,
    )
    geo_optimization_start_dt = fields.Datetime(
        "Optimization task start time",
        help="Date and time the optimization task was submitted to the "
        "TourSolver service.",
        readonly=True,
    )
    geo_optimization_status = fields.Char(
        "Optimization status",
        help="Status of the optimization task provided byt the TourSolver " "service.",
        readonly=True,
    )
    geo_optimization_state = fields.Selection(
        string="Optimization state",
        selection=[
            ("in_progress", "In progress"),
            ("aborted", "Aborted"),
            ("error", "Error"),
            ("success", "Success"),
        ],
        readonly=True,
        compute="_compute_geo_optimization_state",
    )
    geo_optimization_enabled = fields.Boolean("Enable geo optimization")
    geo_optimization_resource_id = fields.Selection(
        selection="_selection_geo_optimization_resource_id"
    )
    geo_optimization_result = fields.Binary(attachment=True, readonly=True)
    geo_optimization_request = fields.Binary(attachment=True, readonly=True)

    geo_optimization_json = fields.Serialized(compute="_compute_geo_optimization_json")
    geo_optimization_error_message = fields.Text("Optimization error message")

    state = fields.Selection(
        selection_add=[
            ("optimizing", "Optimizing delivery"),
            ("optimization_failure", "Delivery Optimization Failure"),
        ]
    )
    warehouse_id = fields.Many2one(
        comodel_name="stock.warehouse", compute="_compute_warehouse_id"
    )

    @api.model
    def _selection_geo_optimization_resource_id(self):
        return self.env["round.template"]._selection_geo_optimization_resource_id()

    @api.constrains("geo_optimization_enabled", "geo_optimization_resource_id")
    def _check_geo_optimization_resource_id(self):
        for rec in self:
            if rec.geo_optimization_enabled and not rec.geo_optimization_resource_id:
                raise ValidationError(
                    _(
                        "A resource identifier is required if geo_optimization is enabled for %s"
                    )
                    % rec.display_name
                )

    @api.depends("geo_optimization_result")
    def _compute_geo_optimization_json(self):
        """The json is computed from the binary fields to allows the download
        of the file from the form view
        """
        for record in self:
            val = {}
            if record.geo_optimization_result:
                val = json.loads(base64.b64decode(record.geo_optimization_result))
            record.geo_optimization_json = val

    @api.depends("geo_optimization_status")
    def _compute_geo_optimization_state(self):
        for record in self:
            status = record.geo_optimization_status
            status = status and status.lower()
            if not status:
                state = False
            elif status in ("error", "failed"):
                state = "error"
            elif status == "aborted":
                state = "cancelled"
            elif status == "terminated":
                state = "success"
            elif status in (
                "undefined",
                "waiting",
                "geocoding",
                "mileageChartBuilding",
                "running",
                "sectorizationRunning",
                "sectorizationFinished",
                "sectorizationAborted",
            ):
                state = "in_progress"
            else:
                raise ValueError("unknow optimization status %s" % status)
            record.geo_optimization_state = state

    @api.depends("shipping_ids")
    def _compute_warehouse_id(self):
        for record in self:
            warehouse_id = record.picking_ids[0].location_id.get_warehouse().id
            record.warehouse_id = self.env["stock.warehouse"].browse(warehouse_id)

    @api.model
    def create(self, vals):
        if "geo_optimization_enabled" not in vals and "template_id" in vals:
            template = self.env["round.template"].browse(vals["template_id"])
            vals["geo_optimization_enabled"] = template.geo_optimization_enabled
            vals["geo_optimization_resource_id"] = template.geo_optimization_resource_id
        return super(RoundInstance, self).create(vals)

    @api.onchange("template_id")
    def onchange_template_id(self):
        super(RoundInstance, self).onchange_template_id()
        for record in self:
            record.geo_optimization_enabled = (
                record.template_id.geo_optimization_enabled
            )

    def _deliver(self, background=True):
        self.filtered(lambda a: a._is_geo_optimization_enabled())._geo_optimize()
        res = super(RoundInstance, self)._deliver(background=background)
        return res

    def _compute_stat_time_loading(self):
        """
        Overrides to add the delivery duration into the expected loading time
        of the truck
        """
        stat_time_loading = super(RoundInstance, self)._compute_stat_time_loading()
        opti_duration = (
            self._is_geo_optimization_enabled()
            and self.get_optimization_config().duration
        )
        if not opti_duration:
            return stat_time_loading
        tz_name = self.env.context.get("tz") or self.env.user.tz
        if not tz_name:
            raise UserError("Please configure your timezone in your user preferences")
        m, s = divmod(opti_duration, 60)
        now = fields.Datetime.context_timestamp(self, datetime.now())
        now = now + timedelta(minutes=m, seconds=s)
        return now.hour + (now.minute / 60.0)

    @api.multi
    def _is_geo_optimization_enabled(self):
        self.ensure_one()
        return self.geo_optimization_enabled and self.get_optimization_config().enabled

    @api.model
    def get_optimization_config(self):
        return self.env["stock.config.settings"].get_optimization_config()

    def _geo_optimize(self):
        self.env.user.notify_info(_("Optimization requests sent to external system."))
        cfg = self.get_optimization_config()
        for record in self:
            optimization_request = record._generate_optimization_request()
            task_id = record._send_optimization_request(optimization_request)
            if task_id:
                record.write(
                    {
                        "geo_optimization_task_id": task_id,
                        "geo_optimization_start_dt": fields.Datetime.now(),
                        "geo_optimization_status": "undefined",
                        "geo_optimization_result": False,
                        "geo_optimization_error_message": False,
                        "geo_optimization_request": base64.b64encode(
                            json.dumps(optimization_request)
                        ),
                    }
                )
                record._delay_check_optimization_status(
                    eta_delay_seconds=cfg.duration + 10
                )
                record.recheck_delivery_state()

    @api.multi
    def button_done(self):
        res = super(RoundInstance, self).button_done()
        for record in self:
            if not record.state == "done":
                continue
            if record._is_geo_optimization_enabled():
                if not record.geo_optimization_state:
                    # optimization not launched; relaunch
                    self._geo_optimize()
                    record.state = "optimizing"
                    continue
                if record.geo_optimization_state == "success":
                    continue
                if record.geo_optimization_state == "in_progress":
                    record.state = "optimizing"
                else:
                    record.state = "optimization_failure"
        return res

    @job(default_channel="root.background.stock_picking_deliver")
    @api.multi
    def recheck_delivery_state(self):
        to_optimize = self.filtered(lambda a: a._is_geo_optimization_enabled())
        super(RoundInstance, self - to_optimize).recheck_delivery_state()
        for record in to_optimize:
            if not record._is_all_customer_delivered():
                continue
            if record.geo_optimization_state == "success":
                record.write({"state": "delivering"})
                super(RoundInstance, record).recheck_delivery_state()
            elif record.geo_optimization_state == "in_progress":
                record.write({"state": "optimizing"})
            elif record.geo_optimization_state in ("aborted", "error"):
                record.write({"state": "optimization_failure"})
            else:
                raise ValueError(
                    "Unexpected geo optimization state %s"
                    % record.geo_optimization_state
                )
        return None

    @api.multi
    def retry_optimization(self):
        """ Relaunch the optimization process for round instance with
        optimization failure or done
        """
        self.filtered(
            lambda r: r.state in ("optimization_failure", "done")
        )._geo_optimize()

    @api.multi
    def button_ignore_optimization_failure(self):
        records = self.filtered(lambda r: r.state in ("optimization_failure"))
        records.write({"geo_optimization_enabled": False})
        records._deliver()

    @api.multi
    def _get_partners_to_deliver(self):
        """
        Return the list of partners who will be delivered.
        We takes as predicate that a partner for which at least one move into
        a picking 'PICK' is done will be delivered
        """
        self.ensure_one()
        sql = """
            SELECT
                distinct sp.partner_id
            FROM
                stock_picking sp,
                stock_picking_type spt,
                stock_move sm
            WHERE
                sm.picking_id = sp.id
                AND sp.picking_type_id = spt.id
                AND spt.subcode='PICK'
                AND sp.delivery_round_id = %s
                AND sm.state='done'
        """
        self.env.cr.execute(sql, (self.id,))
        ids = [i[0] for i in self.env.cr.fetchall()]
        return self.env["res.partner"].browse(ids)

    def _generate_optimization_request(self):
        """Generate the JSON optimization request conform to
        https://geoservices.geoconcept.com/ToursolverCloud/
        api-book.html#_json_optimizerequest
        """
        self.ensure_one()
        cfg = self.get_optimization_config()
        ret = self._generate_optimization_metas(cfg)
        ret["depots"] = self._generate_optimization_depots(cfg)
        ret["orders"] = self._generate_optimization_orders(cfg)
        ret["resources"] = self._generate_optimization_resources(cfg)
        ret["options"] = self._generate_optimization_options(cfg)
        ret["language"] = self.env.user.lang
        ret["simulationName"] = self.display_name
        return ret

    def _generate_optimization_metas(self, cfg):
        return {
            "simulationName": self.display_name,
            "countryCode": "BE",
            "beginDate": self._date_to_geo_date(self.date),
            "language": self.env.user.lang,
        }

    def _generate_optimization_depots(self, cfg):
        address = self.warehouse_id.partner_id
        return [
            {
                "x": address.partner_longitude,
                "y": address.partner_latitude,
                "id": "dep_%s" % address.id,
            }
        ]

    def _generate_optimization_orders(self, cfg):
        ret = []
        partners = self._get_partners_to_deliver()
        delivery_windows_by_partner_id = partners.get_delivery_windows(
            "%s" % datetime.today().weekday()
        )
        for partner in partners:
            phones = filter(None, (partner.mobile or None, partner.phone or None))

            order = {
                "customerId": partner.ref,
                "fixedVisitDuration": seconds_to_duration(partner.delivery_duration),
                "id": partner.id,
                "label": partner.display_name,
                "phone": "| ".join(phones),
                "type": 0,  # delivery,
                "x": partner.partner_longitude,
                "y": partner.partner_latitude,
            }

            customDataMap = {}
            if partner.comment:
                customDataMap["notes"] = partner.comment
            if not all(
                char == "" or char.isspace()
                for char in partner.contact_address.split("\n")
            ):
                customDataMap["address"] = partner.contact_address
            if customDataMap:
                order["customDataMap"] = customDataMap

            delivery_windows = delivery_windows_by_partner_id[partner.id]
            if delivery_windows:
                time_windows = []
                for window in delivery_windows:
                    time_windows.append(
                        {
                            "beginTime": window.float_to_time_repr(window.start),
                            "endTime": window.float_to_time_repr(window.end),
                        }
                    )
                order["timeWindows"] = time_windows
            ret.append(order)
        return ret

    def _generate_optimization_resources(self, cfg):
        address = self.warehouse_id.partner_id
        pattern = "%02d:%02d:00"
        hour = math.floor(self.stat_time_loading)
        min = round((self.stat_time_loading % 1) * 60)
        if min == 60:
            min = 0
            hour += 1

        work_start_time = pattern % (hour, min)
        h, m = divmod(cfg.loading_duration, 60)
        fixed_loading_duration = "%02d:%02d:00" % (h, m)
        return [
            {
                "id": self.geo_optimization_resource_id,
                "mobileLogin": "%s@alcyonbelux.be"
                % self.geo_optimization_resource_id.lower(),
                "startX": address.partner_longitude,
                "startY": address.partner_latitude,
                "endX": address.partner_longitude,
                "endY": address.partner_latitude,
                "openStart": False,  # begin the tour at the resource start location.
                "workStartTime": work_start_time,
                "fixedLoadingDuration": fixed_loading_duration,
                "loadBeforeDeparture": True,
                "noReload": True,
                "globalCapacity": 9999,
                "useAllCapacities": False,
            }
        ]

    def _generate_optimization_options(self, cfg):
        return {
            "vehicleCode": "deliveryIntermediateVehicle",
            "maxOptimDuration": seconds_to_duration(cfg.duration),
        }

    def _send_optimization_request(self, json_request):
        """
        send the optimization request to TourSolver API
        https://geoservices.geoconcept.com/ToursolverCloud/api-book.html
        #_resource_toursolverwebservice_optimize_post
        """
        self.ensure_one()
        action = "optimize"
        optimize_url = self._get_opitization_api_url(action)
        response = requests.post(
            optimize_url, json=json_request, headers={"Accept": "application/json"}
        )
        result = self._check_optimization_response(action, response)
        if result is False:
            return
        return result["taskId"]

    @job(default_channel="root.background.geo_optimization")
    def _check_optimization_status(self):
        """
        Get optimization request status from TourSolver API
        https://geoservices.geoconcept.com/ToursolverCloud/api-book.html
        #_resource_toursolverwebservice_getstatus_get
        """
        self.ensure_one()
        action = "status"
        status_url = self._get_opitization_api_url(
            action, taskId=self.geo_optimization_task_id
        )
        response = requests.get(status_url, headers={"Accept": "application/json"})
        result = self._check_optimization_response(action, response)
        if result is False:
            return
        self.geo_optimization_status = result["optimizeStatus"]
        if self.geo_optimization_state == "in_progress":
            self._delay_check_optimization_status(eta_delay_seconds=20)
        elif self.geo_optimization_state == "success":
            self._get_optimization_result()
        elif self.geo_optimization_state == "error" and result.get("message"):
            self.geo_optimization_error_message = result["message"]
        self.recheck_delivery_state()

    def _get_optimization_result(self):
        """
        Get optimization request result from TourSolver API
        https://geoservices.geoconcept.com/ToursolverCloud/api-book.html
        #_resource_toursolverwebservice_getresult_get
        """
        self.ensure_one()
        action = "result"
        result_url = self._get_opitization_api_url(
            action, taskId=self.geo_optimization_task_id
        )
        response = requests.get(result_url, headers={"Accept": "application/json"})
        result = self._check_optimization_response(action, response)
        if result is False:
            return
        self.geo_optimization_result = base64.b64encode(json.dumps(result))
        self._validate_optimization_result(result)
        self._sort_round_instance_customers()

    def _sort_round_instance_customers(self):
        """
        Sort the list of customer instances according to the list of deliveries
        into the opimization result
        """
        self.ensure_one()
        if self.geo_optimization_state != "success" or not self.geo_optimization_result:
            self.instance_customer_ids._propagate_rank()
            self.instance_customer_ids.write({"is_rank_computed": False})
            return
        expected_partner_order = self._get_planned_partner_ids(
            self.geo_optimization_json
        )
        for round_instance_customer in self.instance_customer_ids:
            partner_id = round_instance_customer.partner_id.id
            rank = -1
            if partner_id in expected_partner_order:
                rank = expected_partner_order.index(partner_id) + 1
            round_instance_customer.write({"rank": rank, "is_rank_computed": True})

    def _notify_optimization_error(self, message):
        self.env.user.notify_warning(
            message=message,
            title=_("%s: Optimization api call failed") % self.display_name,
            sticky=True,
        )

    def _delay_check_optimization_status(self, eta_delay_seconds):
        """
        Delay the check_optimization status

        eta_delay: The delay in seconds tu use for eta
        """
        eta = datetime.now() + timedelta(seconds=eta_delay_seconds)
        description = _("Check geo optimization status for %s") % self.display_name
        self.with_delay(eta=eta, description=description)._check_optimization_status()

    def _check_optimization_response(self, action, response, ignoreError=False):
        """
        Check if the response is OK and process error according
        Return json content if OK otherwise False
        """
        try:
            self.geo_optimization_error_message = False
            response.raise_for_status()
        except requests.HTTPError as http_error:
            msg = "\n".join(filter(None, [http_error.message, response.content]))
            self.geo_optimization_error_message = msg
            self._notify_optimization_error(self.geo_optimization_error_message)
            _logger.exception(
                "Optimization action '%s' of %s failed", action, self.display_name
            )
            if not ignoreError:
                self.geo_optimization_status = "failed"
            return False
        result = response.json()
        if result["status"] == "ERROR":
            self.geo_optimization_error_message = result["message"]
            if not ignoreError:
                self.geo_optimization_status = "failed"
            self._notify_optimization_error(self.geo_optimization_error_message)
            return False
        return result

    def _get_opitization_api_url(self, action, **url_params):
        cfg = self.get_optimization_config()
        baseurl = cfg.api_url
        url_params = url_params or {}
        url_params["tsCloudApiKey"] = cfg.api_key
        url_parts = list(urlparse.urlparse(baseurl))
        url_parts[2] = url_parts[2] + action
        url_parts[4] = urllib.urlencode(url_params)
        return urlparse.urlunparse(url_parts)

    def _validate_optimization_result(self, result):
        """
        Check that all the shiping's partner are into the optimization result
        """
        self.ensure_one()
        expected_partners = set(self._get_partners_to_deliver().ids)
        received_partners = set(self._get_planned_partner_ids(result))
        missing_partners = self.env["res.partner"].browse(
            list(expected_partners - received_partners)
        )
        unexpected_partner_ids = list(received_partners - expected_partners)
        error_messages = []
        if missing_partners:
            error_messages.append(
                _(
                    "The following partners are not found into the "
                    "optimization result: %s"
                )
                % ", ".join(missing_partners.mapped("name"))
            )
        if unexpected_partner_ids:
            error_messages.append(
                _(
                    "The following partner ids are not expected into the "
                    "optimization result: %s"
                )
                % ", ".join(["%s" % i for i in unexpected_partner_ids])
            )
        if error_messages:
            self.write(
                {
                    "geo_optimization_status": "failed",
                    "geo_optimization_error_message": "\n".join(error_messages),
                }
            )

    @api.model
    def _get_planned_partner_ids(self, json_result):
        """
        Return the list of planned partners in the same order as in the json document
        """
        return [
            int(o["stopId"])
            for o in json_result["plannedOrders"]
            if o["stopId"].isdigit()
        ]

    def button_export_to_mobile_app(self):
        """
        Makes the delivery round available into the mobile APP
        """
        return self._delay_export_optimization_to_operational_planning()

    def _delay_export_optimization_to_operational_planning(self):
        """
        Delay the export of the result of an optimization to operational
        planning
        """
        for record in self:
            self.env.user.notify_info(
                _(
                    "The delivery round %s will be exported to tha mobile App into background."
                )
                % record.display_name
            )
            description = (
                _("Export optimization result to operational planning for %s")
                % record.display_name
            )
            record.with_delay(
                description=description
            )._export_optimization_to_operational_planning()

    @job(default_channel="root.background.geo_optimization")
    def _export_optimization_to_operational_planning(self):
        """
        Exports the result of an optimization to operational planning that
        mobile resources will be able to browse on the field through a mobile
        app.
        This command only works on completed optimizations.
        https://geoservices.geoconcept.com/ToursolverCloud/api-book.html
        #_resource_toursolverwebservice_exporttooperationplanning_post
        """
        self.ensure_one()
        background = self.env.context.get("job_uuid") and not config["test_enable"]
        if self.geo_optimization_state != "success":
            error_message = (
                _("Can't export a not complete optimization for %s") % self.display_name
            )
            if background:
                return error_message
            else:
                raise UserError(error_message)

        action = "exportToOperationalPlanning"
        json_request = self._generate_optimization_operational_export_request()
        url = self._get_opitization_api_url(action)
        response = requests.post(
            url, json=json_request, headers={"Accept": "application/json"}
        )
        result = self._check_optimization_response(action, response, ignoreError=True)
        if result is False:
            if background:
                return self.geo_optimization_error_message
            return False
        self.env.user.notify_info(
            _("Optimization for %s exported to operational planning.")
            % self.display_name
        )
        return json_request

    def _generate_optimization_operational_export_request(self):
        self.ensure_one()
        return {
            "taskId": self.geo_optimization_task_id,
            "resourceMapping": [
                {
                    "id": self.geo_optimization_resource_id,
                    "operationalId": "%s@alcyonbelux.be"
                    % self.geo_optimization_resource_id.lower(),
                }
            ],
            "force": True,  # override if exists
            "startDate": self._date_to_geo_date(self.date),
            "dayNums": [1],
        }

    @api.model
    def _date_to_geo_date(self, d):
        """
        Return date as YYYY-MM-DD
        """
        date = fields.Date.from_string(d)
        return date.strftime("%Y-%m-%d")
