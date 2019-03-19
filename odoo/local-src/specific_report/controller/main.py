# -*- coding: utf-8 -*-
# Copyright 2018 Jacques-Etienne Baudoux (BCIM sprl) <je@bcim.be>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import StringIO

import qrcode
from odoo.http import Controller, request, route
from werkzeug import exceptions


class SpecificReportController(Controller):
    @route(['/report/qrcode'], type='http', auth="public")
    def report_qrcode(self, value, size=5, border=4):
        """
        Contoller able to render qrcode images without reportlab.
        <img t-att-src="'/report/qrcode/?value=%s&amp;size=10&amp;border=4' %
            o.name)"/>
        """
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=size,
                border=border,
            )
            qr.add_data(value)
            qr.make(fit=True)
            img = qr.make_image(fill_color="white", back_color="black")
            output = StringIO.StringIO()
            img.save(output, 'png')
            png = output.getvalue()
            output.close()
        except (ValueError, AttributeError):
            raise exceptions.HTTPException(
                description='Cannot convert into qrcode.'
            )
        return request.make_response(
            png, headers=[('Content-Type', 'image/png')]
        )
