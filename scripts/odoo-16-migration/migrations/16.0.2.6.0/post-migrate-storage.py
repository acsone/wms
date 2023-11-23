# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

from psycopg2.extensions import AsIs

from odoo import api

_logger = logging.getLogger(__name__)


def migrate_product_media(cr):
    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    # create a temporary column in fs_product_media to store the old storage file id
    for model in ["alc.eshop.ads", "alc.classified", "alc.eshop.cms.news"]:
        table = model.replace(".", "_")

        _logger.info(
            "Create ir_attachment records from storage_file linked to one %s", model
        )
        cr.execute(
            """
                INSERT INTO ir_attachment (
                    name,
                    type,
                    res_model,
                    res_id,
                    res_field,
                    create_uid,
                    create_date,
                    write_uid,
                    write_date,
                    store_fname,
                    mimetype,
                    file_size,
                    checksum,
                    fs_storage_id,
                    fs_url,
                    fs_storage_code,
                    fs_filename
                )
                SELECT
                    f.name,
                    'binary',
                    '%(model)s',
                    m.id,
                    'file',
                    f.create_uid,
                    f.create_date,
                    f.write_uid,
                    f.write_date,
                    concat('fsprd_eshop://', f.slug),
                    f.mimetype,
                    f.file_size,
                    f.checksum,
                    %(storage_id)s,
                    f.url,
                    'fsprd_eshop',
                    f.slug
                FROM
                    storage_file as f,
                    %(table)s as m
                WHERE
                    m.file_id = f.id
        """,
            {"model": model, "table": AsIs(table), "storage_id": fs_storage_id},
        )

        _logger.info("%s ir_attachment records created", cr.rowcount)


def migrate_cms_news_image(cr):
    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    _logger.info(
        "Create ir_attachment records from storage_image linked to alc.eshop.cms.news"
    )
    cr.execute(
        """
            INSERT INTO ir_attachment (
                name,
                type,
                res_model,
                res_id,
                res_field,
                create_uid,
                create_date,
                write_uid,
                write_date,
                store_fname,
                mimetype,
                file_size,
                checksum,
                fs_storage_id,
                fs_url,
                fs_storage_code,
                fs_filename
            )
            SELECT
                f.name,
                'binary',
                'alc.eshop.cms.news',
                alc_eshop_cms_news.id,
                'thumbnail_image',
                f.create_uid,
                f.create_date,
                f.write_uid,
                f.write_date,
                concat('fsprd_eshop://', f.slug),
                f.mimetype,
                f.file_size,
                f.checksum,
                %s,
                f.url,
                'fsprd_eshop',
                f.slug
            FROM
                alc_eshop_cms_news,
                storage_image as s,
                storage_file as f
            WHERE
                alc_eshop_cms_news.thumbnail_image_id = s.id
                AND s.file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)


def migrate_cms_ads_image(cr):
    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    _logger.info(
        "Create ir_attachment records from storage_image linked to alc.eshop.ads"
    )
    cr.execute(
        """
            INSERT INTO ir_attachment (
                name,
                type,
                res_model,
                res_id,
                res_field,
                create_uid,
                create_date,
                write_uid,
                write_date,
                store_fname,
                mimetype,
                file_size,
                checksum,
                fs_storage_id,
                fs_url,
                fs_storage_code,
                fs_filename
            )
            SELECT
                f.name,
                'binary',
                'alc.eshop.ads',
                alc_eshop_ads.id,
                'image',
                f.create_uid,
                f.create_date,
                f.write_uid,
                f.write_date,
                concat('fsprd_eshop://', f.slug),
                f.mimetype,
                f.file_size,
                f.checksum,
                %s,
                f.url,
                'fsprd_eshop',
                f.slug
            FROM
                alc_eshop_ads,
                storage_image as s,
                storage_file as f
            WHERE
                alc_eshop_ads.image_id = s.id
                AND s.file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

    env = api.Environment(cr, 1, {})
    for adds in env["alc.eshop.ads"].search([]):
        with env.cr.savepoint():
            try:
                adds.image_medium = adds.image
                env.cr.flush()
            except Exception:
                _logger.Info(
                    "Error generating thumbnail for %s: Image %s not found at url",
                    (adds.name, adds.image.name, adds.image.url),
                )


def migrate(cr, version):
    migrate_product_media(cr)
    migrate_cms_news_image(cr)
    migrate_cms_ads_image(cr)
