# -*- coding: utf-8 -*-
# Copyright 2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import job


class Sale(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[("confirm_background", "Confirm in Background")]
    )

    @job(default_channel="root.priority.sale_confirm")  # priority=1
    @api.multi
    def confirm_in_background(self, notify=True):
        """Confirm sales order in background

        The ODOO_QUEUE_JOB_CHANNELS configuration must configure the
        channel for this job as "sequential", so they are processed
        in order of creation, even if jobs are retried.
        If a job fails, the others jobs will wait.

        Configuration: ``root.priority.sale_confirm:1:sequential``
        """
        self.ensure_one()
        if self.state != "confirm_background":
            return
        if self.is_delayed(fields.Datetime.from_string(self.create_date)):
            self.action_cancel()
            self.message_post(
                body=_(
                    "Was automatically cancelled on confirmation because"
                    "the job took longer to execute than the customer allows."
                )
            )
            return
        self.action_confirm()
        if notify:
            action = self.env.ref("sale.action_orders").read()[0]
            action.update({"res_id": self.id, "views": [(False, "form")]})
            self.env.user.notify_info(
                _("Order %s is now confirmed.") % self.name, sticky=True, action=action
            )

    def action_confirm_background(self):
        # compatibility with sale_exception
        # we want to raise interactively, not in background
        if self.detect_exceptions():
            return self._popup_exceptions()
        self.write({"state": "confirm_background"})
        for order in self:
            if not order.confirmation_date:
                order.confirmation_date = fields.Datetime.now()
            self.env.user.notify_info(
                _("Order %s will be confirmed in background.") % order.name
            )
            order.with_delay(
                description=_("Confirmation of sales order %s") % order.name, priority=1
            ).confirm_in_background(notify=False)

    @job(default_channel="root.priority.sale_confirm")
    @api.multi
    def remove_delivery_block(self, notify=True):
        """ Job that execute the remove delivery block on sale order"""
        self.ensure_one()
        if self.state != "confirm_background":
            return
        self.state = "sale"
        super(Sale, self).action_remove_delivery_block()
        if notify:
            action = self.env.ref("sale.action_orders").read()[0]
            action.update({"res_id": self.id, "views": [(False, "form")]})
            self.env.user.notify_info(
                _("Remove delivery block for order %s is now done.") % self.name,
                action=action,
            )

    @api.multi
    def action_remove_delivery_block(self):
        """Make 'Remove the delivery block' asynchronous."""
        for order in self.filtered(lambda s: s.state == "sale"):
            order.write({"state": "confirm_background"})
            self.env.user.notify_info(
                _("Remove delivery block for order %s will be done in background.")
                % order.name
            )
            order.with_delay(
                description=_("Remove delivery block for sales order %s") % order.name,
                priority=1,
            ).remove_delivery_block(notify=True)
