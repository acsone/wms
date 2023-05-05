# Copyright 2019 Camptocamp SA
# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields

from odoo.addons.sale_exception.models import sale_order_line


class SaleOrderLine(sale_order_line.SaleOrderLine):

    exception = fields.Char(compute="_compute_exception")
    warning_text = fields.Char(compute="_compute_exception")

    @api.depends("product_id", "price_subtotal", "order_id.partner_id")
    def _compute_exception(self):
        """Compute sale exceptions and warnings on a line.

        The first exception raised is kept to be displayed on the line.
        Warning text are added to the description of the line.
        """
        line_exceptions = self.env["exception.rule"].search(
            [("model", "=", "sale.order.line")], order="sequence"
        )
        for line in self:
            exception = warning = ""
            if line.product_id:
                for rule in line_exceptions:
                    if not self.env["sale.order"]._rule_eval(rule, line):
                        continue
                    warning += "\n" + rule.description
                    if not exception:
                        exception = rule.description
            line.exception = exception
            if (line.warning_text or "") != (warning or ""):
                line.warning_text = warning
                line.set_line_name()

    def set_line_name(self):
        """Set the name description on the line.

        As there is a column with product code on the SO/invoice, do not put
        internal code prefix on the line description. This rule applies for
        SO and Invoice at product onchange as invoice line description is
        copied from SO line description.
        """
        self.ensure_one()
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )
        name = product.name
        if product.description_sale:
            name += "\n" + product.description_sale
        self.name = (name or "") + (self.warning_text or "")

    @api.onchange("product_id")
    def product_id_onchange(self):
        """It was a 2nd on change method for product_id in v10.

        The other onchange method calls super which raises problems
        with the compute methods being called before defaults fields are
        set by Odoo
        """
        self.set_line_name()
