# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64
import io
import logging
import os
import tempfile
import zipfile

import shapefile
from shapely.geometry import shape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from shapely.wkb import loads as wkbloads

from odoo import Command, _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv.expression import AND, OR

from odoo.addons.alc_stock_release_channel_tag.models.alc_stock_release_channel_tag import (
    AlcStockReleaseChannelTag,
)

from ..models.alc_delivery_plan import AlcDeliveryPlan

_logger = logging.getLogger(__name__)


class AlcImportDeliveryZoneWizard(models.TransientModel):

    _name = "alc.import.delivery.zone.wizard"
    _description = "Import Delivery Zones Wizard"

    delivery_plan_id = fields.Many2one[AlcDeliveryPlan](
        string="Delivery Plan",
        required=True,
        default=lambda x: x._default_delivery_plan(),
    )
    filename = fields.Char()
    file = fields.Binary(string="Import shape file", required=True)
    stock_release_channel_tag_ids = fields.Many2many[AlcStockReleaseChannelTag](
        string="Release channel tags",
        relation="alc_import_channel_tag_rel",
    )

    def _get_zip_file(self):
        zip_data = base64.decodebytes(self.file)
        fp = io.BytesIO()
        fp.write(zip_data)
        return fp

    def button_import(self):
        self.ensure_one()
        self._process_content(self._get_zip_file())

    def _iter_shape_record(self, content):
        """Read the Shape file content and return an iterator on shape_record.

        :param content: Shape file as Zip archive
        :return: shape_record
        """
        self.ensure_one()
        if not content:
            raise UserError(_("No file sent."))
        if not zipfile.is_zipfile(content):
            raise UserError(_("File is not a zip file!"))
        with zipfile.ZipFile(content, "r") as zf:
            tmpdir = tempfile.mkdtemp()
            try:
                zf.extractall(tmpdir)
                for root, _dirs, file_names in os.walk(tmpdir, topdown=True):
                    filename = file_names[0].split(".")[0]
                    path_to_shape_file = os.path.join(root, filename)
                    # Read shapefile
                    with shapefile.Reader(path_to_shape_file) as shp:
                        yield from shp
            except Exception as error:
                _logger.error(error)
                raise UserError(_("Unable to import the shape file")) from error

    def _get_existing_channels(self, channel_name=None):
        domain = [("delivery_plan_id", "=", self.delivery_plan_id.id)]
        if channel_name:
            domain = AND(
                [
                    domain,
                    OR(
                        [
                            [("name", "=", channel_name)],
                            [("shape_name", "=", channel_name)],
                        ]
                    ),
                ],
            )

        return self.env["stock.release.channel"].search(domain)

    def _process_content(self, content):
        self.ensure_one()
        channel_model = self.env["stock.release.channel"]
        existing_channels = self._get_existing_channels()
        new_channels = channel_model

        for shape_record in self._iter_shape_record(content):
            new_channels += self._create_or_update_release_channel(shape_record)

        # Some channels may be rendered useless by the new plan.
        # But they may not be removed if they are required by other models
        to_archives = existing_channels - new_channels
        to_archives.write({"active": False})

    def _get_delivery_zone(self, shape_record):
        delivery_zone = shape(shape_record.shape)
        self.env.cr.execute(  # Use the right projection for shape
            "SELECT ST_TRANSFORM(ST_GeomFromText(%s, 4326), 3857)", (delivery_zone.wkt,)
        )
        projected_geoshape = self.env.cr.fetchone()
        delivery_zone = wkbloads(projected_geoshape[0], hex=True)
        if isinstance(delivery_zone, Polygon):
            # Cast Polygon to MultiPolygon for consistency
            # Some templates have a multipolygon shape, others have a polygon shape
            delivery_zone = MultiPolygon([delivery_zone])
        return delivery_zone

    def _get_delivery_zone_name(self, shape_record):
        name = shape_record.record.Nom
        if not name and hasattr(shape_record.record, "District"):
            name = shape_record.record.District
        return name

    def _create_or_update_release_channel(self, shape_record):
        channel_model = self.env["stock.release.channel"]
        delivery_zone = self._get_delivery_zone(shape_record)
        shape_name = self._get_delivery_zone_name(shape_record)
        existing_channel = self._get_existing_channels(channel_name=shape_name)
        if existing_channel:
            existing_channel.write(
                self._get_channel_values(
                    shape_name=shape_name, delivery_zone=delivery_zone
                )
            )
            return existing_channel
        return channel_model.create(
            self._get_channel_values(
                shape_name=shape_name,
                delivery_zone=delivery_zone,
                channel_name=shape_name,
            )
        )

    def _get_channel_values(self, shape_name, delivery_zone, channel_name=None):
        vals = {
            "shape_name": shape_name,
            "delivery_plan_id": self.delivery_plan_id.id,
            "restrict_to_delivery_zone": True,
            "delivery_zone": delivery_zone,
        }
        if channel_name:
            vals["name"] = channel_name
        if self.stock_release_channel_tag_ids:
            vals["stock_release_channel_tag_ids"] = [
                Command.set(self.stock_release_channel_tag_ids.ids)
            ]
        return vals

    @api.model
    def _default_delivery_plan(self):
        active_model = self.env.context.get("active_model")
        active_id = self.env.context.get("active_id")
        if active_model == "alc.delivery.plan" and active_id:
            return self.env[active_model].browse(active_id)
        return None
