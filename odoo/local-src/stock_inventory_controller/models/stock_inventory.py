import logging

from odoo import api, fields, models
import odoo
from odoo.exceptions import MissingError, UserError

_logger = logging.getLogger(__name__)


class StockInventoryLine(models.Model):
    _inherit = 'stock.inventory.line'

    is_line_failed = fields.Boolean(
        'Line failed',
        readonly=True,
        default=False
    )
    fail_message = fields.Char(
        'Fail message',
        readonly=True,
    )


class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    failed_line_ids = fields.One2many(
        'stock.inventory.line',
        'inventory_id',
        string='Failed inventories',
        domain=[('is_line_failed', '=', True)],
        copy=False,
        readonly=True,
        states={'done': [('readonly', True)]}
    )

    line_ids = fields.One2many(
        domain=[('is_line_failed', '=', False)]
    )

    @api.multi
    def post_inventory(self):
        """
        This method has the api multi but this method is called for each line.
        :return:
        """
        moves = self.mapped('move_ids').filtered(
            lambda move: move.state != 'done')

        with api.Environment.manage():
            with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                new_self = self.with_env(self.env(cr=new_cr))
                exception = False
                for move in moves:
                    try:
                        move.action_done()
                    except MissingError as me:
                        _logger.error('MissingError: ' + str(me))
                        line = new_self.line_ids.search(
                            [('product_id', '=', move.product_id.id)])
                        line.write({
                            'is_line_failed': True,
                            'fail_message': 'MissingError: ' + str(me)
                        })
                        exception = me
                    except UserError as ue:
                        _logger.error('UserError: ' + str(ue))
                        line = new_self.line_ids.search(
                            [('product_id', '=', move.product_id.id)])
                        line.write({
                            'is_line_failed': True,
                            'fail_message': 'UserError: ' + str(ue)
                        })
                        exception = ue
                if exception:
                    new_cr.commit()
                    raise exception
