# -*- coding: utf-8 -*-
# © 2017-2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, models


class StockPackOperation(models.Model):
    _inherit = "stock.pack.operation"
    _rec_name = "product_id"

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (
                    rec.id,
                    "%s (%d/%d)"
                    % (rec.product_id.display_name, rec.qty_done, rec.product_qty),
                )
            )
        return result

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        """Search a pack operation by name

        It is customized to find an operation by the display name of a product.
        The default name_search would search on the pack operation's name_get,
        which would be pretty inefficient due to the products' quantities in
        the name_get.

        This method also handles a fast path for when we are receiving products
        for a picking: in the reception wizard (stock.pack.operation.lot.add),
        the Many2one for stock.pack.operation filters on the picking_id. In
        that case, we limit the search on the products of the picking only.
        """
        args = args or []
        if name:
            # fast path for stock.pack.operation.lot.add, narrow the search
            # on the current picking
            picking_id = None
            product_args = []
            # default limit for search products a too large limit would be too
            # slow when the name match thousands of products
            product_limit = 100
            for (field, op, value) in args:
                if field == "picking_id" and op == "=":
                    picking_id = value
                    break
            if picking_id:
                picking = self.env["stock.picking"].browse(picking_id).exists()
                picking_products = picking.mapped("move_lines.product_id")
                product_args.append(("id", "in", picking_products.ids))
                # in this particular case we can disable the limit as we want
                # all the products of the picking, and we shouldn't have
                # thousands of them matching a term for a picking
                product_limit = None

            product_ids = [
                pid
                for pid, __ in self.env["product.product"].name_search(
                    name, operator=operator, args=product_args, limit=product_limit
                )
            ]
            args = [("product_id", "in", product_ids)] + args
        # Warning: as we limit on 100 products, if filter the pack operations
        # with 'args' and the name returns thousands of products (like 'a'),
        # then potentially we might have an empty list because the 'args'
        # domain would be applied on a list which does not include our product.
        # This is not a problem when using the fast path which should be the
        # common case.
        return self.search(args, limit=limit).name_get()
