# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate_thumbnail(cr):
    _logger.info("Create Seach Engine Thumbnails")
    # create a temporary column in es_thumbail to store the old storage file id
    cr.execute("ALTER TABLE se_thumbnail ADD COLUMN x_old_storage_file_id integer")

    # create se_thumbnail records for storage_thumbnail with size x in (550, 300, 60)
    # The sizes are the one used for the website only
    # create thumb for fs_image
    cr.execute(
        """
    WITH attachment_id_file_id AS (
    SELECT
        att.id,
        fs.x_old_storage_file_id
    FROM
        ir_attachment AS att
    JOIN
        fs_image fs
    ON
        fs.id = att.res_id
        AND att.res_model='fs.image'
        AND att.res_field='image'
    )
    INSERT INTO se_thumbnail (
        size_x,
        size_y,
        mimetype,
        name,
        base_name,
        attachment_id,
        create_uid,
        create_date,
        write_date,
        x_old_storage_file_id
    )
    SELECT
        size_x,
        size_y,
        file_thumbnail.mimetype,
        file_thumbnail.name,
        th_info.url_key AS base_name,
        att.id AS attachment_id,
        th_info.create_uid,
        th_info.create_date,
        th_info.write_date,
        file_thumbnail.id AS x_old_storage_file_id
    FROM
        storage_thumbnail th_info
        JOIN storage_image image_origin ON th_info.res_id =image_origin.id
        JOIN storage_file file_origin ON image_origin.file_id = file_origin.id
        JOIN storage_file file_thumbnail ON th_info.file_id=file_thumbnail.id
        JOIN fs_image as fs_image_origin ON fs_image_origin.x_old_storage_file_id = file_origin.id
        JOIN attachment_id_file_id AS att ON att.x_old_storage_file_id = file_origin.id
    WHERE size_x IN (550, 300, 60)
    """
    )
    _logger.info("%s se_thumbnail records created", cr.rowcount)

    # create thumb for fs_product_image
    cr.execute(
        """
    WITH attachment_id_file_id AS (
        SELECT
            att.id,
            fs.x_old_storage_file_id
        FROM
            ir_attachment AS att
        JOIN
            fs_product_image fs
        ON
            fs.id = att.res_id
            AND att.res_model='fs.product.image'
            AND att.res_field='specific_image'
    )
    INSERT INTO se_thumbnail (
        size_x,
        size_y,
        mimetype,
        name,
        base_name,
        attachment_id,
        create_uid,
        create_date,
        write_date,
        x_old_storage_file_id
    )
    SELECT
        size_x,
            size_y,
            file_thumbnail.mimetype,
            file_thumbnail.name,
            th_info.url_key AS base_name,
            att.id AS attachment_id,
            th_info.create_uid,
            th_info.create_date,
            th_info.write_date,
            file_thumbnail.id AS x_old_storage_file_id
    FROM
        storage_thumbnail th_info
        JOIN storage_image image_origin ON th_info.res_id =image_origin.id
        JOIN storage_file file_origin ON image_origin.file_id = file_origin.id
        JOIN storage_file file_thumbnail ON th_info.file_id=file_thumbnail.id
        JOIN fs_product_image as fs_image_origin on fs_image_origin.x_old_storage_file_id = file_origin.id
        JOIN attachment_id_file_id AS att ON att.x_old_storage_file_id = file_origin.id
        WHERE size_x IN (550, 300, 60)
    """
    )
    _logger.info("%s se_thumbnail records created", cr.rowcount)

    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    # create ir_attachment records for storage_thumbnail with size x in (550, 300, 60)
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
                'se.thumbnail',
                se_thumbnail.id,
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
                storage_file as f,
                se_thumbnail
            WHERE
                se_thumbnail.x_old_storage_file_id = f.id
    """,
        (fs_storage_id,),
    )
    _logger.info("%s ir_attachment records created", cr.rowcount)


def migrate(cr, version):
    migrate_thumbnail(cr)
