# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
import io
import logging
import os
import zipfile

import shapefile
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.osutil import tempdir
from shapely.geometry import asShape
from shapely.geometry.multipolygon import MultiPolygon
from shapely.geometry.polygon import Polygon
from shapely.wkb import loads as wkbloads

logger = logging.getLogger(__name__)


class ShapeFileImportWizard(models.TransientModel):

    _name = "shape.file.import.wizard"

    filename = fields.Char()
    shape_file = fields.Binary(string="Import shape file", required=True)
    delivery_plan_id = fields.Many2one(
        "delivery.plan", default=lambda x: x._default_delivery_plan_id()
    )

    @api.model
    def _default_delivery_plan_id(self):
        return self.env["delivery.plan"].browse(self.env.context.get("active_ids")).id

    @api.multi
    def execute_import(self):
        self.ensure_one()

        # Retrieve ZIP file
        zip_data = base64.decodestring(self.shape_file)
        fp = io.BytesIO()
        fp.write(zip_data)

        # Process zip content
        self._process_content(fp)

    @api.multi
    def _iter_shape_record(self, content):
        """ Read the Shape file content and return an iterator on shape_record
        :param content: Shape file as Zip archive
        :return: shape_record
        """
        self.ensure_one()
        if not content:
            raise Exception(_("No file sent."))
        if not zipfile.is_zipfile(content):
            raise UserError(_("File is not a zip file!"))

        with zipfile.ZipFile(content, "r") as z, tempdir() as tmpdir:
            try:
                z.extractall(tmpdir)
                files = []
                for root, dirs, file_names in os.walk(tmpdir, topdown=True):
                    files.extend(file_names)
                    filename = files[0].split(".")[0]
                    path_to_shape_file = os.path.join(root, filename)
                    # Read shapefile
                    with shapefile.Reader("%s" % path_to_shape_file) as shp:
                        for shape_record in shp:
                            yield shape_record
            except Exception:
                msg = _("Unable to import the shape file")
                logger.exception(msg)
                raise UserError(_("Unable to import the shape file"))

    @api.multi
    def _process_content(self, content):
        self.ensure_one()

        existing_template_ids = set(self.delivery_plan_id.round_template_ids.ids)
        new_template_ids = set()

        for shape_record in self._iter_shape_record(content):
            new_template_ids.add(self._create_or_update_round_template(shape_record).id)

        # Remove templates that does not exist anymore
        self.env["round.template"].browse(
            existing_template_ids - new_template_ids
        ).unlink()

    @api.multi
    def _create_or_update_round_template(self, shape_record):
        geo_shape = asShape(shape_record.shape)

        # Use the right projection for shape
        self.env.cr.execute(
            "SELECT ST_TRANSFORM(\
                                ST_GeomFromText(%s, 4326), 3857)",
            (geo_shape.wkt,),
        )
        projected_geoshape = self.env.cr.fetchone()
        wkb = wkbloads(projected_geoshape[0], hex=True)

        # Cast Polygon to MultiPolygon for consistency
        # Some templates have a multipolygon shape, others have a polygon shape
        if isinstance(wkb, Polygon):
            wkb = MultiPolygon([wkb])

        existing_template = self.delivery_plan_id.round_template_ids.filtered(
            lambda x: x.name == shape_record.record.Nom
        )
        if existing_template:
            # Update template
            existing_template.write(
                {
                    "geo_polygon_shape": wkb,
                    "geo_optimization_resource_id": shape_record.record.Nom,
                }
            )
            return existing_template

        else:
            # Create template
            return self.env["round.template"].create(
                {
                    "name": shape_record.record.Nom,
                    "delivery_plan_id": self.delivery_plan_id.id,
                    "geo_optimization_resource_id": shape_record.record.Nom,
                    "geo_polygon_shape": wkb,
                }
            )
