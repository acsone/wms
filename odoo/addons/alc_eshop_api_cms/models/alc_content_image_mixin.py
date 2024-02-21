# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import re

from werkzeug.routing import Map, Rule

from odoo.addons.alc_eshop_cms import models

IMG_RULES = [
    "/web/image/<string:xmlid>",
    "/web/image/<string:xmlid>/<string:filename>",
    "/web/image/<string:xmlid>/<int:width>x<int:height>",
    "/web/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>",
    "/web/image/<int:id>",
    "/web/image/<int:id>/<string:filename>",
    "/web/image/<int:id>/<int:width>x<int:height>",
    "/web/image/<int:id>/<int:width>x<int:height>/<string:filename>",
    "/web/image/<int:id>-<string:unique>",
    "/web/image/<int:id>-<string:unique>/<string:filename>",
    "/web/image/<int:id>-<string:unique>/<int:width>x<int:height>",
    "/web/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>",
]

IMAGE_URL_MAP = Map([Rule(r) for r in IMG_RULES])
URL_MAPPER = IMAGE_URL_MAP.bind("localhost")


class AlcContentImageMixin(models.AlcContentImageMixin):
    def _get_content(self):
        """Return html content and ensure images are published."""
        content = self.content
        for match in re.finditer(r'<img src="(/[^"]+)"', content):
            url = match.group(1)
            if not url.startswith("/web/image/"):
                continue
            # ensure image is published
            result = URL_MAPPER.match(url)
            if not result:
                continue
            args = result[1]
            _id = None
            if args.get("id"):
                _id = int(args["id"])
            xmlid = args.get("xmlid")
            attachment = None
            if xmlid:
                attachment = self.env.ref(xmlid)
            elif _id:
                attachment = self.env["ir.attachment"].browse(_id)
            if not attachment:
                continue
            thumbnail = attachment.sudo()._get_or_create_thumbnail()
            public_url = thumbnail.image.url or ""
            content = content.replace(url, public_url)
        return content
