import logging
from contextlib import contextmanager

import odoo
from odoo import _, api, exceptions, fields, models

_logger = logging.getLogger(__name__)


class InventoryError(Exception):
    """Error happening during action_done() of the inventory

    errors is a list of (line, exception raised by the line)
    """

    def __init__(self, errors, msg=None):
        if not msg:
            msg = _("Error during Inventory")
        super(InventoryError, self).__init__(msg)
        self.errors = errors


class StockMove(models.Model):
    _inherit = "stock.move"

    inventory_line_id = fields.Many2one(comodel_name="stock.inventory.line")


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    is_line_failed = fields.Boolean("Line failed", readonly=True, default=False)
    fail_message = fields.Char("Fail message", readonly=True)

    def _get_move_values(self, qty, location_id, location_dest_id):
        values = super(StockInventoryLine, self)._get_move_values(
            qty, location_id, location_dest_id
        )
        values["inventory_line_id"] = self.id
        return values


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    failed_line_ids = fields.One2many(
        "stock.inventory.line",
        "inventory_id",
        string="Failed inventories",
        domain=[("is_line_failed", "=", True)],
        copy=False,
        readonly=True,
        states={"done": [("readonly", True)]},
    )

    line_ids = fields.One2many(domain=[("is_line_failed", "=", False)])

    @api.multi
    def action_done(self):
        @contextmanager
        def open_new_env():
            with api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    yield self.env(cr=new_cr)

        # save the state before we create and validate moves
        try:
            return super(StockInventory, self).action_done()
        except InventoryError as err:
            bullets = []
            # Open a new cursor to save the error in the lines, as we'll
            # raise the error after, it will rollback everything.
            with open_new_env() as new_env:
                for line, original_error in err.errors:
                    bullets.append(
                        u" - %s: %s"
                        % (line.product_id.display_name, original_error.name)
                    )

                    line = line.with_env(new_env)
                    # If the line does not exist in the new cr, it means
                    # that it has been created in the same transaction:
                    # either in a unit test, either by the wizard
                    # "stock.change.product.qty". We don't care about
                    # writing back the failure message in these cases,
                    # because the inventory and its lines will be
                    # rollbacked with the main transaction anyway
                    if not line.exists():
                        continue
                    line.write(
                        {"is_line_failed": True, "fail_message": original_error.name}
                    )

            raise exceptions.UserError(
                _(u"Cannot validate inventory:\n\n%s") % ("\n".join(bullets),)
            )

    @api.multi
    def post_inventory(self):
        """
        This method has the api multi but this method is called for each line.
        :return:
        """
        moves = self.mapped("move_ids").filtered(lambda move: move.state != "done")
        errors = []
        for move in moves:
            try:
                move.action_done()
            except exceptions.UserError as err:
                _logger.error("UserError: %s", err)
                line = move.inventory_line_id
                if not line:
                    # This is only in case we are trying to validate an
                    # inventory started before and validated after we added the
                    # field 'inventory_line_id' in the addon. Can be removed
                    # once we have deployed the addon sinc 'inventory_line_id' will
                    # always be populated then.
                    raise exceptions.UserError(
                        _("Error during validation. Please restart an inventory.")
                    )
                errors.append((line, err))
        if errors:
            raise InventoryError(errors)
