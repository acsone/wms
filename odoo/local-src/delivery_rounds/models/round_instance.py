# -*- coding: utf-8 -*-
# © 2016-2017 Jacques-Etienne Baudoux (BCIM)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from ast import literal_eval
import math
from contextlib import contextmanager, closing
from datetime import datetime
from itertools import groupby
import psycopg2

import odoo
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import config

from odoo.addons.queue_job.job import job

import logging
_logger = logging.getLogger(__name__)


def float2time(value):
    hour = math.floor(value)
    minute = round((value % 1) * 60)
    if (minute == 60):
        minute = 0
        hour = hour + 1
    return '%d:%02d' % (hour, minute)


def time2float(value):
    return value.hour + value.minute / 60.0


def time_now(record):
    tz_name = record.env.context.get('tz') or record.env.user.tz
    if not tz_name:
        raise UserError(
            "Please configure your timezone in your user preferences")
    return time2float(fields.Datetime.context_timestamp(
        record, datetime.now()))


class RoundInstance(models.Model):
    _name = 'round.instance'
    _order = 'date desc, time_picking_planned asc'
    _rec_name = 'complete_name'

    date = fields.Date(
        'Date',
        required=True,
        states={'done': [('readonly', True)],
                'delivering': [('readonly', True)]},
        default=fields.Date.context_today)

    time_picking_planned = fields.Float(
        'Planned Picking Start Time',
        states={'done': [('readonly', True)],
                'delivering': [('readonly', True)]},
        )
    time_leave_planned = fields.Float(
        'Planned Vehicle Start Time',
        states={'done': [('readonly', True)],
                'delivering': [('readonly', True)]},
        )

    stat_time_closed = fields.Float(
        'Closed Time', readonly=True)
    stat_time_picking = fields.Float(
        'Picking Start Time', readonly=True)
    stat_time_leave = fields.Float(
        'Vehicle Start Time', readonly=True)

    template_id = fields.Many2one(
        'round.template', 'Template',
        states={'done': [('readonly', True)]},
        required=True,
        ondelete='restrict')
    template_code = fields.Char(
        'Code',
        related='template_id.code',
        store=True,
        readonly=True
    )
    template_name = fields.Char(
        'Name',
        related='template_id.name',
        store=True,
        readonly=True
    )
    color = fields.Integer(
        related='template_id.color')
    state = fields.Selection(
        [('pending', 'Anticipated'),
         ('draft', 'Open'),
         ('close', 'Closed'),
         ('delivering', 'Delivering'),
         ('done', 'Done')],
        'State',
        readonly=True,
        default='pending')
    picking_launched = fields.Boolean(
        'Pickings Launched',
        readonly=True)

    itinerary_ids = fields.Many2many(
        'round.itinerary',
        string="Itineraries",
        readonly=True)

    picking_ids = fields.One2many(
        'stock.picking', 'delivery_round_id', 'Pickings',
        domain=[('picking_type_subcode', '=', 'PICK')],
        readonly=True,
        )
    shipping_ids = fields.One2many(
        'stock.picking', 'delivery_round_id', 'Deliveries',
        domain=[('picking_type_code', '=', 'outgoing')],
        readonly=True,
        )

    complete_name = fields.Char(
        'Display Name', readonly=True,
        compute='_get_complete_name', store=True)
    tag_ids = fields.Many2many('round.tag', string='Tags')
    partner_ids = fields.Many2many(
        'res.partner',
        string='Partners',
        readonly=True,
        compute='_compute_partner_ids',
        search='_search_partner_ids'
    )
    instance_customer_ids = fields.One2many(
        comodel_name='round.instance.customer',
        inverse_name='delivery_round_id',
        string='Customers',
        states={'done': [('readonly', True)],
                'delivering': [('readonly', True)]},
    )
    delivery_failure = fields.Boolean(
        compute='_compute_delivery_failure'
    )
    report_delivery = fields.Html(
        compute='_compute_report_delivery',
        readonly=True,
    )

    @api.depends('instance_customer_ids.picking_state_ids.state')
    @api.multi
    def _compute_delivery_failure(self):
        for record in self:
            record.delivery_failure = any(
                state.state == 'failed'
                for icust in record.instance_customer_ids
                for state in icust.picking_state_ids
            )

    @api.depends('instance_customer_ids.picking_state_ids.message')
    @api.multi
    def _compute_report_delivery(self):
        for record in self:
            lines = []
            for customer in record.instance_customer_ids:
                if customer.delivered or not customer.report:
                    continue
                lines.append({
                    'customer': customer,
                    'report': customer.report,
                })
            if lines:
                record.report_delivery = self.env.ref(
                    'delivery_rounds.round_report_delivery'
                ).render({'round': record, 'customers': lines})

    @api.multi
    def _compute_partner_ids(self):
        for instance in self:
            partners = instance.mapped(
                'itinerary_ids.partner_position_ids.partner_id'
            )
            instance.partner_ids = [(6, 0, partners.ids)]

    def _search_partner_ids(self, operator, value):
        """
        Search for template containing the customer name
        :param operator:
        :param value:
        :return:
        """

        positions = self.env['round.itinerary.position'].search(
            [('partner_id.name', operator, value)])
        itineraries = self.env['round.itinerary'].search(
            [('partner_position_ids', 'in', positions.ids)]
        )

        return [('itinerary_ids', 'in', itineraries.ids)]

    @api.multi
    @api.depends('template_id', 'date', 'time_leave_planned')
    def _get_complete_name(self):
        for rec in self:
            rec.complete_name = '%s %s - %s' % (
                rec.date,
                float2time(rec.time_leave_planned),
                rec.template_id.display_name)

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            vals = name.split('-', 1)
            if len(vals) > 1:
                code = vals[0].strip()
                text = vals[1].strip()
                comb = operator.startswith('not ') and '|' or '&'
            else:
                code = text = name.strip()
                comb = operator.startswith('not ') and '&' or '|'
            domain = [
                comb,
                ('template_code', operator, code),
                ('template_name', operator, text)]
        records = self.search(domain + args, limit=limit)
        return records.name_get()

    @api.multi
    def button_itinerary_import(self):
        return dict(self.env.ref(
            'delivery_rounds.action_round_itinerary_import').read()[0])

    @api.multi
    def button_update(self):
        for record in self:
            record._include_itinerary(self.itinerary_ids)

    def _include_itinerary(self, itineraries):
        self.ensure_one()

        self.itinerary_ids |= itineraries

        partners = itineraries.mapped('partner_position_ids.partner_id')
        # Itineraries can contain partner of any type. So extract corresponding
        # delivery address
        partners_delivery_ids = [partner.address_get(['delivery'])['delivery']
                                 for partner in partners]

        picking_confirmed = self.env['stock.picking'].search([
            ('delivery_round_id', '=', False),
            ('partner_id', 'in', partners_delivery_ids),
            ('state', '=', 'confirmed')])
        self._assign_pickings(picking_confirmed)

    def _assign_pickings(self, pickings, no_prepare=False):
        self.ensure_one()
        _logger.debug("Assign to round instance %s the pickings %s",
                      self.id, pickings.ids)

        pickings.filtered(
            lambda picking: picking.state == 'draft').action_confirm()
        # Note: MTO moves in waiting state are updated in standard by a call to
        # action_assign, so we need to propagate it
        moves = pickings.mapped('move_lines').filtered(
            lambda move: move.state in ('waiting', 'confirmed') and
            not move.linked_move_operation_ids)
        if moves:
            moves.with_context(round_autoset=False).action_assign(
                no_prepare=no_prepare)

        # retrieve all pickings (partially) available
        pickings_assigned = self.env['stock.picking'].search([
            ('id', 'in', pickings.ids),
            ('state', 'in', ('partially_available', 'assigned'))])
        if pickings_assigned:
            def key(r):
                partner = r.partner_id
                # If delivery address is a contact, take parent
                if partner.type == 'contact' and partner.parent_id:
                    partner = partner.parent_id
                return partner

            for partner, pickings_bypartner_iter in groupby(
                    pickings_assigned.sorted(key=key), key=key):
                ric = self._add_customer(partner)
                pickings_bypartner = reduce(
                    lambda x, y: x | y, pickings_bypartner_iter)
                ric._link_pickings(pickings_bypartner)
        return pickings_assigned

    @api.multi
    def _add_customer(self, customer):
        self.ensure_one()
        customer.ensure_one()
        ric = self.env['round.instance.customer'].search([
            ('delivery_round_id', '=', self.id),
            ('partner_id', '=', customer.id),
            ('delivered', '!=', True)])
        rank = 0
        if not ric:
            pos = self.env['round.itinerary.position'].search([
                ('itinerary_id', 'in', self.itinerary_ids.ids),
                ('partner_id', '=', customer.id)])
            if pos:
                rank = (pos.sequence + pos.itinerary_id.sequence*1000) * 1000
            _logger.warn("Partner added on delivery %s", self.id)
            ric = self.env['round.instance.customer'].sudo().create({
                'delivery_round_id': self.id,
                'partner_id': customer.id,
                'rank': rank,
                })
        return ric

    @api.model
    def find_bytemplate(self, template):
        """
        Find a delivery_round for having a specified template. This is used for
        deliveries linked to a specific carrier
        """
        return self.search([
                ('template_id', '=', template.id),
                ('state', 'not in', ('delivering', 'done')),
            ],
            order='date asc, time_leave_planned asc',
            limit=1,
        )

    @api.model
    def find_bypartner(self, partner):
        """
        Find a delivery_round for this partner according to tags defined
        on customer position or round instance.
        Round instances are sorted according to the date and the time of
        the picking.

        Here is the rule for taking or not a round instance:
        - If you define one (or more) tag on the instance, only customer
        containing this tag will be taken
        - A customer without tag will be taken in any case

        :param partner:
        :return:
        """
        if not partner:
            # This should not happen unless a picking without partner has been
            # manually created
            return False

        _logger.debug("Search a round instance for partner %s", partner.id)

        # The following query will search for the best itinerary instance.
        # First, the query will search for all open instance (state = draft)
        # The itinerary linked to this instance must contains the partner
        # (round_instance_round_itinerary_rel).
        # In this case, we will check tags on the customer (customer_tag)
        # and the instance tag (instance_tag).
        # Info: A customer and/or instance can have several tags.
        # In this case the query will return several lines.
        #
        # Tags rules:
        # - The customer tag must be equal to the instance tag
        # - The customer tag is empty
        # - The instance tag is empty

        # If delivery address is a contact, take parent
        if partner.type == 'contact' and partner.parent_id:
            partner = partner.parent_id

        best_instance_query = """
        SELECT instance.id
        FROM round_instance_round_itinerary_rel AS rel
          INNER JOIN round_instance AS instance
            ON rel.round_instance_id = instance.id
          INNER JOIN round_itinerary_position AS position
            ON position.itinerary_id = rel.round_itinerary_id
          INNER JOIN res_partner AS customer
            ON position.partner_id = customer.id
          LEFT JOIN round_instance_round_tag_rel AS instance_tag
            ON instance.id = instance_tag.round_instance_id
          LEFT JOIN round_itinerary_position_round_tag_rel AS customer_tag
            ON position.id = customer_tag.round_itinerary_position_id
        WHERE instance.state = 'draft'
          AND (instance_tag.round_tag_id = customer_tag.round_tag_id
              OR customer_tag IS NULL
              OR instance_tag IS NULL)
          AND customer.id = %s
        ORDER BY instance.date DESC, instance.time_picking_planned ASC
        LIMIT 1;
        """

        self.env.cr.execute(best_instance_query, (partner.id, ))
        result = self.env.cr.fetchone()

        if result:
            _logger.debug("Instance found with ID %s", result[0])
            return self.browse(result[0])

        return False

    count_picking_available_total = fields.Integer(
        'Picking Available Total',
        compute='_get_count_picking',
        readonly=True)
    count_picking_done_total = fields.Integer(
        'Picking Done Total',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_partner = fields.Integer(
        'Picking Available Partner',
        compute='_get_count_picking',
        readonly=True)
    count_picking_available_weight = fields.Integer(
        'Picking Available Total',
        compute='_get_count_weight',
        readonly=True)

    @api.depends('picking_ids')
    def _get_count_weight(self):
        self._cr.execute("""
            SELECT picking.delivery_round_id,
            sum(coalesce(product_template.weight, 0) *
                coalesce(stock_pack_operation.product_qty, 0))
            FROM stock_picking picking
            LEFT JOIN stock_picking_type
                ON picking.picking_type_id = stock_picking_type.id
            LEFT JOIN stock_pack_operation
                ON stock_pack_operation.picking_id = picking.id
            LEFT JOIN product_product
                ON stock_pack_operation.product_id = product_product.id
            LEFT JOIN product_template
                ON product_product.product_tmpl_id = product_template.id
            WHERE picking.state IN ('partially_available', 'assigned', 'done')
            AND stock_picking_type.subcode = 'PICK'
            AND picking.delivery_round_id in %s
            GROUP BY picking.delivery_round_id
            """, (tuple(self.ids), ))
        for r in self._cr.fetchall():
            self.browse(r[0]).count_picking_available_weight = r[1]

    @api.depends('picking_ids')
    def _get_count_picking(self):
        for rec in self:
            rec.count_picking_done_total = len(rec.picking_ids.filtered(
                lambda r: r.state == ('done')))
            pickings = rec.picking_ids.filtered(
                lambda r: r.state in ('partially_available', 'assigned',
                                      'done'))
            rec.count_picking_available_total = len(pickings)
            rec.count_picking_available_partner = \
                len(pickings.mapped('partner_id'))

    @api.multi
    def action_picking_tree_available(self):
        action = self.env['ir.actions.act_window'].for_xml_id(
            'delivery_rounds', 'action_picking_tree_available_round'
        )

        domain_str = action.get('domain', "[]")
        domain = literal_eval(domain_str)

        domain += [('state', '!=', 'cancel')]
        action['domain'] = domain

        return action

    @api.multi
    def toggle_picking_launched(self):
        started = self.filtered('picking_launched')
        stopped = self - started
        started.button_picking_stop()
        stopped.button_picking_start()

    @api.multi
    def button_picking_start(self):
        """ Pickings can be processed """
        for rec in self:
            rec.picking_launched = True
            if not rec.stat_time_picking:
                rec.stat_time_picking = time_now(self)

    @api.multi
    def button_picking_stop(self):
        """ Pickings cannot be processed """
        self.write({'picking_launched': False})

    @api.multi
    def toggle_partner_locked(self):
        opened = self.filtered(lambda r: r.state == 'draft')
        closed = self.filtered(lambda r: r.state == 'close')
        opened.button_close()
        closed.button_resetdraft()

    @api.multi
    def button_close(self):
        """ Do not accept new picking automaticaly.
        """
        not_started = self.filtered(lambda r: not r.picking_launched)
        not_started.button_picking_start()
        self.write({
            'state': 'close',
            'stat_time_closed': time_now(self),
            })

    @api.multi
    def button_deliver(self):
        """ Deliver all customers. This validates all shipping orders that are
        available.
        Mark as done and unlink other deliveries
        """
        icust = self.mapped('instance_customer_ids')
        icust.filtered(lambda c: not c.delivered)._deliver()
        self.state = 'delivering'
        self.env.user.notify_info(
            _('Round will be delivered in background.')
        )
        self.recheck_delivery_state()

    @api.multi
    def button_resetdraft(self):
        """ Mark state as draft. This allows new pickings
        """
        self.write({'state': 'draft'})

    @api.multi
    def button_resetpending(self):
        """ Mark state as draft. This allows new pickings
        """
        self.write({'state': 'pending'})

    @api.multi
    def button_done(self):
        """ Mark as done and unlink waiting deliveries """
        for shipping in self.mapped('shipping_ids'):
            if shipping.state == 'waiting':
                shipping.delivery_round_id = False
        started = self.filtered('picking_launched')
        started.button_picking_stop()
        self.write({
            'state': 'done',
            # TODO move when we start to delay the delivery?
            'stat_time_leave': time_now(self),
            })

    @api.multi
    def print_all_deliveryslip(self):
        shipping_done = self.shipping_ids.filtered(
            lambda shipping: shipping.state == 'done')
        return self.env['report'].get_action(shipping_done,
                                             'stock.report_deliveryslip')

    @api.multi
    def unlink(self):
        if self.mapped('state') != ['draft']:
            raise UserError(_(
                'You cannot delete a delivery round that has been started'))
        pickings = self.mapped('picking_ids')
        res = super(RoundInstance, self).unlink()
        # @api.constrains is not triggered on source model when referenced
        # record is deleted. So let's call it.
        pickings._update_delivery_round()
        return res

    @api.multi
    @api.depends('shipping_ids')
    def _compute_shipping_count(self):
        for shipping in self:
            shipping.shipping_count = len(shipping.shipping_ids)

    shipping_count = fields.Integer(
        compute='_compute_shipping_count',
    )

    @api.multi
    def action_view_shippings(self):
        self.ensure_one()

        action_data = self.env.ref(
            'delivery_rounds.action_picking_tree_round'
        ).read()[0]
        action_data['domain'] = [
            ('picking_type_code', '=', 'outgoing'),
            ('delivery_round_id', '=', self.id),
        ]
        return action_data

    @api.multi
    @api.depends('picking_ids')
    def _compute_picking_count(self):
        for picking in self:
            picking.picking_count = len(picking.picking_ids)

    picking_count = fields.Integer(
        compute='_compute_picking_count',
    )

    @api.multi
    def action_view_pickings(self):
        self.ensure_one()

        action_data = self.env.ref(
            'delivery_rounds.action_picking_tree_round'
        ).read()[0]
        action_data['domain'] = [
            ('picking_type_subcode', '=', 'PICK'),
            ('delivery_round_id', '=', self.id),
        ]
        return action_data

    def cron_recheck_delivery_state(self):
        """Cron that check if a round is fully delivered

        The pickings are processed by jobs. We cannot know what will be the
        last job and 2 jobs could be executed at the end which prevent them to
        transition the round to done.
        A solution could be to implement a chain of dependency jobs in the
        queue job but it isn't possible (yet?). A cheap solution is a cron that
        recheck the state.
        """
        for delivery_round in self.search([('state', '=', 'delivering')]):
            delivery_round.with_delay().recheck_delivery_state()

    @job(default_channel='root.background.delivery')
    @api.multi
    def recheck_delivery_state(self):
        for record in self.exists():
            if record.state != 'delivering':
                continue

            if all(ic.delivered for ic in record.instance_customer_ids):
                # when we transition from not delivered to delivered,
                # we detach the pickings that could not be done
                for icust in record.instance_customer_ids:
                    icust.mapped('picking_ids')._detach_from_round()
                    icust._remove_if_empty()
                # Close delivery round
                record.button_done()


class RoundInstancePickingState(models.Model):
    """ Relation between picking and instance's customer

    It is created when a round is in the process of being
    delivered. When button_deliver is created on the round
    instance, one record per picking is created.

    For each picking, it represents the current state in
    the delivery process:

    * waiting delivery
    * delivery done
    * failure to deliver

    In case of failure, it holds the message for the failure.

    It allows to track the delivery "global" state of a single round:

    * waiting delivery
    * fully delivered
    * failure (at least one picking had a failure)

    This is an internal model, the various information is given
    to the user through the round instance
    """
    _name = 'round.instance.picking.state'
    _description = 'State of a picking in a Round'

    picking_id = fields.Many2one(
        comodel_name='stock.picking',
        required=True,
    )
    instance_customer_id = fields.Many2one(
        comodel_name='round.instance.customer',
        required=True,
        ondelete='cascade',
    )
    state = fields.Selection(
        selection=[
            ('progress', 'Progress'),
            ('done', 'Done'),
            ('failed', 'Failed'),
        ],
        required=True,
        default='progress',
    )
    message = fields.Char()

    _sql_constraints = [
        (
            'unique_customer_picking_id',
            'unique(picking_id, instance_customer_id)',
            _('There is already a delivery in progress for a picking')
        ),
    ]

    @contextmanager
    def _new_env(self, new_cr=True):
        with api.Environment.manage():
            registry = odoo.modules.registry.RegistryManager.get(
                self.env.cr.dbname
            )
            if new_cr:
                with closing(registry.cursor()) as cr:
                    try:
                        yield self.env(cr=cr)
                    except Exception:
                        cr.rollback()
                        raise
                    else:
                        # disable pylint error because this is a valid commit,
                        # we are in a new env
                        if not config['test_enable']:
                            cr.commit()  # pylint: disable=invalid-commit
            else:
                yield self.env()

    @contextmanager
    def _handle_error(self):
        try:
            yield
        except (ValidationError, UserError, AccessError) as err:
            # Do nothing on purpose, failed job should not need
            # user intervention. The record will be marked
            # as failed, users will see it on the round and be able
            # to retry to deliver manually.
            # TODO find why we have concurrent transaction errors
            # that appears as failed with a message, should be retried
            self.write({
                'state': 'failed',
                'message': unicode(err),
            })
            # other kind of exception should still make the job fail
            # so we can discover them and fix them
        else:
            self.write({
                'state': 'done',
                'message': '',
            })

    def _lock(self):
        """Lock the record

        Lock the record so we are sure that only one export
        job is running for this record if concurrent jobs have to export the
        same record.
        When concurrent jobs try to export the same record, the first one
        will lock and proceed, the others will fail to lock and will be
        retried later.
        """
        sql = ("SELECT id FROM %s WHERE ID in %%s FOR UPDATE NOWAIT" %
               self._table)
        record_ids = tuple(self.ids)
        try:
            self.env.cr.execute(sql, (record_ids,), log_exceptions=False)
        except psycopg2.OperationalError:
            _logger.info('A concurrent job is already working on the same '
                         'record. Retry later')
            raise UserError(
                    'A job is already working on the same record. '
                    'You may need to retry later.')

    @job(default_channel='root.background.deliver')
    @api.multi
    def deliver(self, new_cr=True):
        if not self.exists():
            return
        self.ensure_one()
        if self.state == 'done':
            return
        self._lock()
        with self._handle_error():
            with self._new_env(new_cr=new_cr) as new_env:
                self.picking_id.with_env(new_env)._do_round_picking_transfer()
        self.instance_customer_id.delivery_round_id.with_delay()\
            .recheck_delivery_state()


class RoundInstanceCustomer(models.Model):
    _name = 'round.instance.customer'
    _order = 'rank,write_date desc'
    _rec_name = 'partner_id'

    delivery_round_id = fields.Many2one(
        comodel_name='round.instance',
        string='Delivery Round',
        required=True,
        readonly=True,
        index=True,
        ondelete='cascade',
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer',
        required=True,
        readonly=True,
        index=True,
        ondelete='restrict',
        oldname='res_partner_id',
    )
    picking_state_ids = fields.One2many(
        comodel_name='round.instance.picking.state',
        inverse_name='instance_customer_id',
    )

    rank = fields.Integer(
        string='Rank',
    )

    picking_ids = fields.One2many(
        'stock.picking', 'delivery_round_customer_id', 'Pickings',
        readonly=True)

    report = fields.Html(
        compute='_compute_report',
        readonly=True,
    )

    delivered = fields.Boolean(
        'Delivered',
        compute='_compute_delivered',
        search='_search_delivered',
    )

    @api.depends('delivery_round_id.state', 'picking_state_ids.state')
    def _compute_delivered(self):
        for icust in self:
            icust.delivered = (
                icust.delivery_round_id.state in ('delivering', 'done')
                and all(state.state == 'done' for state
                        in icust.picking_state_ids)
            )

    def _search_delivered(self, operator, value):
        if operator not in ('=', '!='):
            return []
        # search the picking states that still need to be done
        not_done_states = self.env['round.instance.picking.state'].read_group(
            [('state', 'in', ('progress', 'failed'))],
            ['instance_customer_id'],
            'instance_customer_id'
        )
        icust_ids = [r['instance_customer_id'][0] for r in not_done_states]
        domain = [
            '|',
            ('delivery_round_id.state', 'not in', ('done', 'delivering')),
            ('id', 'in', icust_ids),
        ]
        not_delivered = self.search(domain)
        if operator == '=':
            condition = 'not in' if value else 'in'
        elif operator == '!=':
            condition = 'in' if value else 'not in'
        return [('id', condition, not_delivered.ids)]

    @api.depends('picking_state_ids.message')
    @api.multi
    def _compute_report(self):
        for record in self:
            lines = []
            for state in record.picking_state_ids:
                if not state.message:
                    continue
                lines.append({
                    'picking': state.picking_id,
                    'message': state.message,
                })
            if lines:
                record.report = self.env.ref(
                    'delivery_rounds.round_customer_report'
                ).render({'round_customer': record, 'pickings': lines})

    @api.multi
    def _link_pickings(self, pickings):
        self.ensure_one()
        # Link all pickings/shippings
        shippings = pickings._get_all_dest_pickings().filtered(
            lambda r: r.picking_type_code == 'outgoing')
        # ensure all related pickings are assigned to the same delivery
        # round
        # Use | to let it work in tests with one step delivery
        pickings |= shippings._get_all_src_pickings()
        # Note that in our case, an open picking cannot have multiple open
        # shippings, so we don't have to ensure a picking is not already done
        # for another delivery round
        pickings = pickings.filtered(
            lambda r: r.state in (
                'waiting',
                'confirmed',
                'partially_available',
                'assigned') and
            r.delivery_round_customer_id.id != self.id)
        if pickings:
            _logger.debug("Link to delivery round the pickings/shippings %s",
                          pickings)
            pickings.with_context(noround_write=True).write({
                'delivery_round_customer_id': self.id,
                'rank': self.rank})

    def _remove_if_empty(self):
        """ Remove partner from round instance if no more pickings or all
        canceled """
        if not self.mapped('picking_ids').filtered(
                lambda p: p.state != 'cancel'):
            _logger.debug(
                "Removing customers %s from round instance %s",
                self.mapped('partner_id').ids,
                self.mapped('delivery_round_id').ids)
            self.unlink()

    @api.multi
    @api.constrains('rank')
    def _propagate_rank(self):
        for instance_customer in self:
            rank = instance_customer.rank
            # when we set a rank on a round instance customer,
            # we copy that value on the pickings
            pickings = self.picking_ids.filtered(lambda p: p.rank != rank)
            if not pickings:
                continue
            _logger.debug(
                "Rank set on round instance customer %s. Propagate to "
                "pickings and shippings %s",
                self.ids, pickings.ids)
            pickings.write({'rank': rank})

    count_picking_progress = fields.Char(
        'Picking Progress',
        compute='_get_count_picking',
        readonly=True)

    @api.depends('picking_ids')
    def _get_count_picking(self):
        for rec in self:
            pickings = rec.picking_ids.filtered(
                lambda r: r.picking_type_subcode == 'PICK')
            count_done = len(pickings.filtered(
                lambda r: r.state == ('done')))
            count_total = len(pickings.filtered(
                lambda r: r.state in ('partially_available', 'assigned',
                                      'done')))
            rec.count_picking_progress = '%s/%s' % (count_done, count_total)

    def button_deliver(self):
        """ Validate all shipping orders that are available """
        self.ensure_one()
        self._deliver(background=False)
        if not self.picking_ids:
            # Nothing was picked, all pickings have been disconnected
            raise UserError(_("No picking have been processed yet"))

    def _deliver(self, background=True):
        """ Validate all shipping orders that are available

        It is done by creating records of round.instance.picking.state,
        each one will be responsible to deliver a picking.
        """
        pickings = self.mapped('picking_ids').filtered(
            lambda p: p.picking_type_code != 'outgoing' and
            # FIXME: some done moves are send to backorder?
            p.state in ('partially_available', 'assigned')
        )
        if any(op.qty_done for op in pickings.mapped('pack_operation_ids')):
            raise UserError(_("You cannot deliver when a picking is ongoing"))

        # start by removing all the states not yet done, so if a picking
        # has been removed or canceled, we won't expect it to be delivered
        # anymore
        self.mapped('picking_state_ids').filtered(
            lambda state: state.state != 'done'
        ).unlink()

        for icust in self:
            for shipping in icust.picking_ids:
                if (shipping.state in ('draft', 'waiting', 'confirmed')
                        or shipping.picking_type_code != 'outgoing'):
                    continue
                elif shipping.state not in ('assigned', 'partially_available'):
                    continue
                state = self.env['round.instance.picking.state'].create({
                    'instance_customer_id': icust.id,
                    'picking_id': shipping.id,
                })
                if background:
                    state.with_delay(
                        description=_(
                            'Deliver shipping %s for round %s'
                        ) % (state.picking_id.name,
                             icust.delivery_round_id.complete_name)
                    ).deliver()
                else:
                    state.deliver()

    def print_deliveryslip(self):
        shippings = self.picking_ids.filtered(
            lambda p: p.picking_type_code == 'outgoing')
        shipping_done = shippings.filtered(
            lambda shipping: shipping.state == 'done')
        return self.env['report'].get_action(shipping_done,
                                             'stock.report_deliveryslip')
