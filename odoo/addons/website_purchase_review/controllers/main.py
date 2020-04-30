# -*- coding: utf-8 -*-
import json
import logging
from datetime import datetime
from urllib import urlencode

from dateutil.relativedelta import relativedelta

from odoo import fields, http
from odoo.addons.web.controllers.main import Home, module_boot
from odoo.http import request
from werkzeug.utils import redirect

_logger = logging.getLogger(__name__)

FILTERS = [
    'products_to_order',
    'products_without_promo',
    'products_with_promo',
    'product_name',
    'next_product_id',
]


class PurchaseReview(Home):
    @http.route(
        [
            '/purchase_review/<model("purchase.order"):po>',
            '/purchase_review/<model("purchase.order"):po>/'
            '<model("product.product"):product>',
        ],
        type='http',
        methods=['GET', 'POST'],
        auth='user',
        website=False,
        csrf=False,
    )
    def purchase_review(self, po, product=None, **kw):
        if not product:
            products = po.get_products()
            if not products:
                raise Exception("There are no products for this supplier")

            product_id = products[0]['id']
            product = request.env['product.product'].browse(product_id)

        params = {}
        for filter in FILTERS:
            value = kw.pop(filter, None)
            if value:
                params[filter] = value
        # Pop debug key to avoid having different results with debug activated
        kw_copy = kw.copy()
        if 'debug' in kw_copy:
            kw_copy.pop('debug')
        if kw_copy:
            po.update_or_create_line(kw_copy)

            if params.get('next_product_id'):
                url = '/purchase_review/{}/{}'.format(
                    po.id, params['next_product_id']
                )
            else:
                url = '/purchase_review/%s' % po.id

            if params:
                url += "?%s" % urlencode(params)

            return redirect(url)

        render_values = {
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            'modules': json.dumps(module_boot()),
            'po': po,
            'res_company': request.env.user.company_id,
            'current_product': product,
            'product_qty': 0,
            'total_weight': po.total_weight,
            'amount_untaxed': po.amount_untaxed,
            'is_confirmed_line': False,
            'is_existing_line': False,
            'return_url': po.get_url(),
        }

        if po.date_planned_overwrite:
            date_planned_overwrite = fields.Datetime.from_string(
                po.date_planned_overwrite
            )
            date_planned_overwrite_str = fields.Date.to_string(
                date_planned_overwrite
            )
            render_values[
                'date_planned_overwrite'
            ] = date_planned_overwrite_str

        if po.discount_global_overwrite:
            render_values[
                'discount_global_overwrite'
            ] = po.discount_global_overwrite

        if po.promotion_supplier_overwrite:
            render_values[
                'promotion_supplier_overwrite'
            ] = po.promotion_supplier_overwrite

        po_line = po.order_line.filtered(
            lambda line: line.product_id == product
        )
        if len(po_line) > 1:
            raise Exception(
                "You can only have one purchase order line by product"
            )

        if po_line:
            date_planned_str = po_line.date_planned
            date_planned = fields.Datetime.from_string(date_planned_str)
            render_values.update(
                {
                    'current_product': product,
                    'product_qty': po_line.product_qty,
                    'price_unit_base': po_line.price_unit_base,
                    'discount_global': po_line.discount_global,
                    'promotion_supplier': po_line.promotion_supplier,
                    'date_planned': fields.Date.to_string(date_planned),
                    'is_existing_line': True,
                    'is_confirmed_line': po_line.is_confirmed_line,
                }
            )
        else:
            seller = product._select_seller(partner_id=po.partner_id)

            # Set the price_unit_base unit base
            price_unit_base = seller.price or 0

            # Set the date planned
            if render_values.get('date_planned_overwrite'):
                date_planned = fields.Datetime.from_string(
                    render_values['date_planned_overwrite']
                )
            elif seller:
                delivery_lead_time = seller.delay
                date_planned = datetime.now() + relativedelta(
                    days=delivery_lead_time
                )
            else:
                date_planned = datetime.now()
            date_planned_str = fields.Date.to_string(date_planned)

            # Set the discount global
            if render_values.get('discount_global_overwrite'):
                discount_global = render_values['discount_global_overwrite']
            else:
                discount_global = po.partner_id.supplier_discount

            # Set the promotion supplier
            if render_values.get('promotion_supplier_overwrite'):
                promotion_supplier = render_values[
                    'promotion_supplier_overwrite'
                ]
            else:
                promotion_supplier = seller.discount_purchase or 0

            render_values.update(
                {
                    'price_unit_base': price_unit_base,
                    'discount_global': discount_global,
                    'promotion_supplier': promotion_supplier,
                    'date_planned': date_planned_str,
                }
            )

        return request.render(
            "website_purchase_review.main_page", render_values
        )
