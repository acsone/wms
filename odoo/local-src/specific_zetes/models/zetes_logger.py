# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ZetesLogger(models.Model):
    _name = 'zetes.logger'

    action = fields.Selection([('requ', 'Request'),
                               ('resp', 'Response'),
                               ('resu', 'Action')],
                              string='Action',
                              required=True)
    domain = fields.Selection([('assignment', 'Assignment'),
                               ('catchweight', 'Catchweight'),
                               ('itempick', 'Itempick'),
                               ('location', 'Location'),
                               ('print', 'Print'),
                               ('refdata', 'refdata'),
                               ('usercontext', 'Usercontext'),
                               ],
                              string='Domain',
                              required=True)
    command = fields.Char('Command',
                          compute='_compute_name',
                          store=True,
                          readonly=True)
    user_id = fields.Many2one('res.users', string='User', required=True)
    name = fields.Char('Name', compute='_compute_name', readonly=True)
    picking_id = fields.Many2one('stock.picking', string='Picking')
    operation_id = fields.Many2one('stock.pack.operation', string='Operation')
    request = fields.Char('Request')
    formatted_request = fields.Char('Request')
    is_checked = fields.Boolean('Checked')
    traceback = fields.Text('Traceback')

    @api.depends('action', 'domain', 'user_id')
    @api.multi
    def _compute_name(self):
        for log in self:
            command_displayed = dict(self._fields['action'].selection)\
                .get(log.action, log.action)
            domain_displayed = dict(self._fields['domain'].selection)\
                .get(log.domain, log.domain)

            name = '{} on {} by {}'.format(command_displayed,
                                           domain_displayed,
                                           log.user_id.name)
            command = '{}_{}'.format(log.action.upper(),
                                     log.domain.upper())
            log.name = name
            log.command = command

    @api.model
    def create(self, vals):
        log = super(ZetesLogger, self).create(vals)

        if log.picking_id:
            log.picking_id.is_zetes_error = True

        return log

    @api.multi
    def toggle_is_checked(self):
        for log in self:
            log.is_checked = not log.is_checked
