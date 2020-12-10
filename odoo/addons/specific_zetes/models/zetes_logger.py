# -*- coding: utf-8 -*-
from odoo import api, fields, models

from .. import constants


class ZetesLogger(models.Model):
    _name = "zetes.logger"
    _order = "create_date desc, id desc"
    _description = "Zetes logger"

    action = fields.Selection(constants.ZETES_ACTIONS, string="Action", required=True)
    domain = fields.Selection(constants.ZETES_DOMAINS, string="Domain", required=True)
    command = fields.Char("Command", compute="_compute_name", store=True, readonly=True)
    user_id = fields.Many2one("res.users", string="User", required=True)
    name = fields.Char("Name", compute="_compute_name", readonly=True)
    picking_id = fields.Many2one("stock.picking", string="Picking", index=True)
    operation_id = fields.Many2one("stock.pack.operation", string="Operation")
    request = fields.Char("Request")
    formatted_request = fields.Text("Request")
    is_checked = fields.Boolean("Checked")
    traceback = fields.Text("Traceback")
    call_stack = fields.Text("Call stack")
    requires_check = fields.Boolean()
    error_type = fields.Selection(
        [("technical", "Technical"), ("human", "Human")],
        string="Error type",
        default="technical",
        required=True,
    )
    to_check = fields.Boolean(compute="_compute_to_check", store=True)

    @api.depends("requires_check", "is_checked")
    def _compute_to_check(self):
        for record in self:
            record.to_check = record.requires_check and not record.is_checked

    @api.depends("action", "domain", "user_id")
    def _compute_name(self):
        """
        Compute a friendly name and the technical name of a command.
        E.g:
        action: requ
        domain: assignment
        user: Admin

        This method will compute the name:
        "Request on Assignement by Admin"
        And the technical name:
        "REQU_ASSIGNMENT"
        :return:
        """
        for log in self:
            command_displayed = dict(constants.ZETES_ACTIONS).get(
                log.action, log.action
            )
            domain_displayed = dict(constants.ZETES_DOMAINS).get(log.domain, log.domain)

            name = u"{} on {} by {}".format(
                command_displayed, domain_displayed, log.user_id.name
            )
            command = u"{}_{}".format(log.action.upper(), log.domain.upper())
            log.name = name
            log.command = command

    @api.model
    def create(self, vals):
        """
        If we log an error linked to a picking
        we will set the flag "is_zetes_error".
        :param vals:
        :return:
        """
        log = super(ZetesLogger, self).create(vals)

        # If the log is linked to a picking, set the flag on this picking
        if log.picking_id:
            log.picking_id.is_zetes_error = True

        return log

    @api.multi
    def toggle_is_checked(self):
        """
        This method is used by the button "Checked" on the form view.
        This method will only change the flag "is_checked".
        is_checked == False => is_checked == True => is_checked == False ...
        :return:
        """
        for log in self:
            log.is_checked = not log.is_checked

    @api.multi
    def button_checked(self):
        for log in self:
            log.is_checked = True
