# -*- coding: utf-8 -*-
# Copyright 2017 Julien Coux (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_line_original = fields.One2many(
        comodel_name='sale.order.line.original',
        inverse_name='order_id',
        string='Original lines',
    )

    order_line_additional = fields.One2many(
        comodel_name='sale.order.line.additional',
        inverse_name='order_id',
        readonly=True,
        string='Original lines',
    )

    order_line_additional_count = fields.Integer(
        compute='_compute_order_line_additional_count',
        readonly=True,
        store=False,
        string='Additional lines count',
    )

    @api.depends('order_line_additional')
    def _compute_order_line_additional_count(self):
        for order in self:
            count = len(order.order_line_additional)
            order.order_line_additional_count = count

    @api.model
    def get_values_for_additional_line(
            self,
            new_product,
            new_quantity,
            additional_product,
            position,
            line
    ):
        return {
            'product_id': new_product.id,
            'product_uom_qty': new_quantity,
            'product_uom': new_product.uom_id.id,
            'additional_line': True,
            'additional_line_is_free': additional_product.is_free,
            'additional_line_position': position,
            'original_line_id': line.id,
        }

    @api.model
    def get_current_values_for_additional_line(self, current_line, line):
        current_values = {
            'product_id': current_line.product_id.id,
            'product_uom_qty': current_line.product_uom_qty,
            'product_uom': current_line.product_uom.id,
            'additional_line': True,
            'additional_line_is_free':
                current_line.additional_line_is_free,
            'additional_line_position':
                current_line.additional_line_position,
            'original_line_id': line.id
        }
        return current_values

    @api.multi
    def compute_additional_line(self):
        """
            With original lines, we compute the additional lines.
            This method check if additional line is modified or not
            and apply the good action :
            - Creation of a new additional line
            - Modification of an existing additional line
            - Deletion of an existing additional line
        """
        self.ensure_one()

        order_line_additional = []

        # For each original line, we check if an additional line is necessary
        for line in self.order_line_original:
            line_product_uom_qty = line.product_uom_qty

            # For each additional line defined on original product,
            # we check if conditions are good to add the additional product
            for additional_product in line.product_id.additional_product_ids:
                original_quantity = additional_product.original_quantity

                # Do we have enough original products to add additional product
                if line_product_uom_qty >= original_quantity:
                    new_template = additional_product.product_id
                    # We get the first variant of product template
                    # because this module doesn't manage product variants
                    # and additional products are defined on product template
                    new_product = new_template.product_variant_ids[0]

                    # Get position of the additional product on sale order
                    position = additional_product.position_on_sale

                    # In function of defined calculation method,
                    # we compute the quantity of the additional product
                    method = additional_product.calculation_method
                    if method == 'once':
                        new_quantity = additional_product.quantity
                    elif method == 'proportional':
                        factor = int(line_product_uom_qty / original_quantity)
                        new_quantity = additional_product.quantity * factor

                    # Get values for the additional line
                    values = self.get_values_for_additional_line(
                        new_product,
                        new_quantity,
                        additional_product,
                        position,
                        line
                    )

                    # Get the existing additional line for the product
                    current_line = self.order_line_additional.filtered(
                        lambda l: (
                            l.original_line_id.id == line.id
                            and l.product_id == new_product
                        )
                    )

                    # Check if the additional line must be :
                    # - added
                    # - modified
                    # - deleted
                    if current_line:

                        # Additional line already exists
                        current_values = (
                            self.get_current_values_for_additional_line(
                                current_line,
                                line
                            )
                        )
                        key_to_delete = []
                        for key, value in values.iteritems():
                            if current_values.get(key) == value:
                                key_to_delete.append(key)
                        for key in key_to_delete:
                            del(values[key])
                        if values:

                            # A value have be changed
                            values = (1, current_line.id, values)
                        else:

                            # All values are identical
                            values = (4, current_line.id)
                    else:

                        # Additional line is a new line
                        values = (0, 0, values)

                    # Add the current additional line to list
                    if values:
                        order_line_additional.append(values)

        # Update the additional lines on the sale order
        # (write method if sale order already saved, update method if not)
        if self.env.context.get('write_values'):

            # The additional lines
            # without link to their original line must be deleted.
            #
            # This case occurs when the original line is deleted.
            # In this case,
            # the link between original line and additional line disappear.
            lines_to_be_deleted = self.order_line_additional.filtered(
                lambda l: (
                    not l.original_line_id
                )
            )

            for line in lines_to_be_deleted:
                order_line_additional.append((3, line.id))

            # If sale order already exists,
            # it's necessary to do a write and not an update,
            # because with an update,
            # odoo try to delete the existing lines
            # before recreate the lines with given values
            self.write({
                'order_line_additional': order_line_additional
            })
        else:
            self.update({
                'order_line_additional': order_line_additional
            })

        # For each additional lines, apply the product_id onchange
        # (to compute all necessary fields)
        # and compute the additional line price
        for line in self.order_line_additional:
            line.product_id_change()
            if line.additional_line_is_free:
                line.price_unit = 0.0

    @api.model
    def get_accepted_fields_for_order_line(self):
        """
            To define accepted fields
            to copy original lines into final lines.
        """
        return ['name', 'product_uom_qty', 'price_unit', 'sequence']

    @api.model
    def get_accepted_relational_fields_for_order_line(self):
        """
            To define accepted relational fields
            to copy original lines into final lines.
        """
        return ['product_id', 'product_uom']

    @api.model
    def get_accepted_relational_m2m_fields_for_order_line(self):
        """
            To define accepted relational Many2many fields
            to copy original lines into final lines.
        """
        return ['tax_id']

    def get_order_lines_values(self, lines, link_field):
        """
        This method used to compute final lines from original/additional lines.
        It's called once for original lines and once for additional lines.
        """
        order_lines = []

        accepted_fields = self.get_accepted_fields_for_order_line()
        accepted_relational_fields = (
            self.get_accepted_relational_fields_for_order_line()
        )
        accepted_relational_m2m_fields = (
            self.get_accepted_relational_m2m_fields_for_order_line()
        )

        # For each original/additional line,
        # we check the changes to apply on the final line.
        for line in lines:
            values = {}
            # Get the current existing field
            final_line = self.order_line.filtered(
                lambda l: l[link_field].id == line.id
            )

            # For each line field, we check if the value has changed.
            # (Only for defined fields)
            for field in line._fields:
                if field in accepted_fields:
                    new_value = line[field]
                    if not final_line or final_line[field] != new_value:
                        values[field] = new_value
                if field in accepted_relational_fields:
                    new_value = line[field]
                    if not final_line or final_line[field] != new_value:
                        values[field] = new_value.id
                if field in accepted_relational_m2m_fields:
                    new_value = line[field]
                    if not final_line or final_line[field] != new_value:
                        values[field] = new_value.ids

            # Check if the final line must be :
            # - added
            # - modified
            # - deleted
            if not final_line:
                # Final line is a new line
                values[link_field] = line.id
                order_lines.append((0, 0, values))
            else:
                if values:
                    # A value have be changed
                    order_lines.append((1, final_line.id, values))
                else:
                    # All values are identical
                    order_lines.append((4, final_line.id))

        # The final lines
        # without link to their original/additional line must be deleted.
        lines_to_be_deleted = self.order_line.filtered(
            lambda l: (
                l[link_field]
                and l[link_field].id not in lines.ids
            )
        )
        for line in lines_to_be_deleted:
            order_lines.append((3, line.id))

        return order_lines

    @api.onchange('order_line_original')
    def onchange_order_line_original(self):

        if not self.order_line_original:
            return

        # Compute additional lines
        self.compute_additional_line()

        # Compute order lines sequences
        sequence = 1

        at_end_lines = []
        lines_original = self.order_line_original.sorted(
            key=lambda l: l.sequence
        )
        for line_original in lines_original:
            line_original.sequence = sequence
            sequence += 1
            lines_additional = self.order_line_additional.filtered(
                lambda l: l.original_line_id.id == line_original.id
            ).sorted(
                key=lambda l: l.sequence
            )
            for line_additional in lines_additional:
                if line_additional.additional_line_position == 'just_after':
                    line_additional.sequence = sequence
                    sequence += 1
                elif line_additional.additional_line_position == 'at_end':
                    at_end_lines.append(line_additional)
        for line in at_end_lines:
            line.sequence = sequence
            sequence += 1

        # Compute final order lines
        order_lines = self.get_order_lines_values(
            self.order_line_original,
            'original_line_id'
        ) + self.get_order_lines_values(
            self.order_line_additional,
            'additional_line_id'
        )

        # Update the additional lines on the sale order
        # (write method if sale order already saved, update method if not)
        if self.env.context.get('write_values'):

            # The final lines
            # without link to their original/additional line must be deleted.
            #
            # This case occurs when the additional line is deleted.
            # In this case,
            # the link between additional line and final line disappear.
            lines_to_be_deleted = self.order_line.filtered(
                lambda l: (
                    not l.original_line_id and not l.additional_line_id
                )
            )
            for line in lines_to_be_deleted:
                order_lines.append((3, line.id))

            # If sale order already exists,
            # it's necessary to do a write and not an update,
            # because with an update,
            # odoo try to delete the existing lines
            # before recreate the lines with given values
            self.write({
                'order_line': order_lines
            })
        else:
            self.update({
                'order_line': order_lines
            })

    @api.model
    def create(self, vals):
        # In case we create a sale order in another module
        # without original lines,
        # we use final lines values as original lines values
        # and we delete the final lines which will computed
        # by the onchange method.
        if vals.get('order_line') and not vals.get('order_line_original'):
            vals['order_line_original'] = vals['order_line']
            del(vals['order_line'])
        record = super(SaleOrder, self).create(vals)
        # Because additional/final lines are readonly,
        # we need to apply the onchange
        # on create to save the correct values.
        #
        # Without that,
        # the additional/final lines aren't sent by form view,
        # and their values aren't save.
        record.with_context(write_values=True).onchange_order_line_original()
        return record

    @api.multi
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        if vals.get('order_line_original'):
            for order in self:
                # Because additional/final lines are readonly,
                # we need to apply the onchange
                # on write to save the correct values.
                #
                # Without that,
                # the additional/final lines aren't sent by form view,
                # and their values aren't save.
                order.with_context(
                    write_values=True
                ).onchange_order_line_original()
        return result

    def fields_view_get(self, cr, user, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        res = super(SaleOrder, self).fields_view_get(
            cr, user, view_id=view_id, view_type=view_type,
            context=context, toolbar=toolbar, submenu=submenu
        )
        # To avoid to define the original/additional lines form view,
        # we use the same form view of final lines
        # as form view of original/additional lines.
        if res['type'] == 'form':
            views = res['fields']['order_line']['views']
            res['fields']['order_line_original']['views'] = views
            res['fields']['order_line_additional']['views'] = views
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    additional_line = fields.Boolean(
        string='Additional line'
    )
    additional_line_is_free = fields.Boolean(
        string='Additional line is free'
    )
    additional_line_position = fields.Char(
        string='Additional line position'
    )

    # To keep link between original/additional lines and final lines
    original_line_id = fields.Many2one(
        comodel_name='sale.order.line.original',
    )
    additional_line_id = fields.Many2one(
        comodel_name='sale.order.line.additional',
    )


# You must override this inherit of sale_product_additional in your
# highest module (the specific module which depends all sale module you need)
# to complete sale.order.line.original with new specific fields
class SaleOrderLineOriginal(models.Model):
    _name = 'sale.order.line.original'
    _inherit = 'sale.order.line'


# You must override this inherit of sale_product_additional in your
# highest module (the specific module which depends all sale module you need)
# to complete sale.order.line.original with new specific fields
class SaleOrderLineAdditional(models.Model):
    _name = 'sale.order.line.additional'
    _inherit = 'sale.order.line'
