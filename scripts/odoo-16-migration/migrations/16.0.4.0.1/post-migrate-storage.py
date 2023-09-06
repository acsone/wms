# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate_product_media(cr):
    # create a temporary column in fs_product_media to store the old storage file id
    cr.execute(
        """
            alter table fs_product_media add column x_old_storage_file_id integer;
            alter table fs_media add column x_old_storage_file_id integer;
        """
    )
    _logger.info("Create fs_product_media records from storage_file")
    cr.execute(
        """
            INSERT INTO  fs_product_media (
                product_tmpl_id,
                x_old_storage_file_id,
                lang,
                sequence,
                write_uid,
                write_date,
                create_uid,
                create_date,
                name,
                mimetype
            )
            SELECT
                r.product_tmpl_id,
                f.id,
                f.lang,
                r.sequence,
                f.write_uid,
                f.write_date,
                f.create_uid,
                f.create_date,
                f.name,
                f.mimetype
            FROM
                product_media_relation as r,
                storage_media as s,
                storage_file as f
            WHERE
                r.media_id = s.id
                AND s.file_id = f.id;
    """
    )
    _logger.info("%s fs_product_media records created", cr.rowcount)

    # create fs_media records for media that are linked to more thant one product_media_relation
    cr.execute(
        """
            INSERT INTO fs_media (
                x_old_storage_file_id,
                lang,
                write_uid,
                write_date,
                create_uid,
                create_date,
                name,
                mimetype
            )
            SELECT
                f.id,
                f.lang,
                f.write_uid,
                f.write_date,
                f.create_uid,
                f.create_date,
                f.name,
                f.mimetype
            FROM
                storage_media as s,
                storage_file as f
            WHERE
                s.file_id = f.id
                AND s.id IN (
                    SELECT
                        media_id
                    FROM
                        product_media_relation
                    GROUP BY
                        media_id
                    HAVING
                        count(*) > 1
                );
    """
    )
    _logger.info("%s fs_media records created", cr.rowcount)

    _logger.info("Link fs_product_media to fs_media")
    cr.execute(
        """
            UPDATE
                fs_product_media as pm
            SET
                media_id = fs_media.id,
                link_existing = True
            FROM
                fs_media
            WHERE
                pm.x_old_storage_file_id = fs_media.x_old_storage_file_id;
    """
    )
    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    _logger.info(
        "Create ir_attachment records from storage_file linked to one product_media_relation"
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
                'fs.product.media',
                fs_product_media.id,
                'specific_file',
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
                product_media_relation as r,
                storage_media as s,
                storage_file as f,
                fs_product_media
            WHERE
                fs_product_media.x_old_storage_file_id = f.id
                AND fs_product_media.media_id is null
                AND r.media_id = s.id
                AND s.file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

    _logger.info(
        "Create ir_attachment records from storage_file linked to one fs_media"
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
                'fs.media',
                fs_media.id,
                'file',
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
                fs_media
            WHERE
                fs_media.x_old_storage_file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)


def migrate_product_image(cr):
    cr.execute(
        """
            alter table fs_product_image add column x_old_storage_file_id integer;
            alter table fs_image add column x_old_storage_file_id integer;
        """
    )
    _logger.info("Create fs_product_image records from storage_file")
    cr.execute(
        """
            INSERT INTO  fs_product_image (
                product_tmpl_id,
                x_old_storage_file_id,
                sequence,
                write_uid,
                write_date,
                create_uid,
                create_date,
                name,
                mimetype
            )
            SELECT
                r.product_tmpl_id,
                f.id,
                r.sequence,
                f.write_uid,
                f.write_date,
                f.create_uid,
                f.create_date,
                f.name,
                f.mimetype
            FROM
                product_image_relation as r,
                storage_image as s,
                storage_file as f
            WHERE
                r.image_id = s.id
                AND s.file_id = f.id;
    """
    )
    _logger.info("%s fs_product_image records created", cr.rowcount)

    # create fs_image records for image that are linked to more thant one product_image_relation
    cr.execute(
        """
            INSERT INTO fs_image (
                x_old_storage_file_id,
                write_uid,
                write_date,
                create_uid,
                create_date,
                name,
                mimetype
            )
            SELECT
                f.id,
                f.write_uid,
                f.write_date,
                f.create_uid,
                f.create_date,
                f.name,
                f.mimetype
            FROM
                storage_image as s,
                storage_file as f
            WHERE
                s.file_id = f.id
                AND s.id IN (
                    SELECT
                        image_id
                    FROM
                        product_image_relation
                    GROUP BY
                        image_id
                    HAVING
                        count(*) > 1
                );
    """
    )
    _logger.info("%s fs_image records created", cr.rowcount)

    _logger.info("Link fs_product_image to fs_image")
    cr.execute(
        """
            UPDATE
                fs_product_image as pm
            SET
                image_id = fs_image.id,
                link_existing = True
            FROM
                fs_image
            WHERE
                pm.x_old_storage_file_id = fs_image.x_old_storage_file_id;
    """
    )
    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    _logger.info(
        "Create ir_attachment records from storage_file linked to one product_image_relation"
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
                'fs.product.image',
                fs_product_image.id,
                'specific_image',
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
                product_image_relation as r,
                storage_image as s,
                storage_file as f,
                fs_product_image
            WHERE
                fs_product_image.x_old_storage_file_id = f.id
                AND fs_product_image.image_id is null
                AND r.image_id = s.id
                AND s.file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

    _logger.info(
        "Create ir_attachment records from storage_file linked to one fs_image"
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
                'fs.image',
                fs_image.id,
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
                fs_image
            WHERE
                fs_image.x_old_storage_file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

    _logger.info("Link main image on product_template")
    cr.execute(
        """
        UPDATE
            product_template
        SET
            main_image_id = sub.id
        FROM (
            SELECT
                fs.id,
                pt.id as product_tmpl_id
            FROM
                fs_product_image fs,
                product_template pt,
                storage_image si
            WHERE
                fs.x_old_storage_file_id = si.file_id
                AND si.id = pt.x_main_image_id
            ) AS sub
        WHERE
            sub.product_tmpl_id = product_template.id;
        """
    )
    _logger.info("%s main image linked", cr.rowcount)

    _logger.info("Link main image on product_product")
    cr.execute(
        """
        UPDATE
            product_product
        SET
            main_image_id = sub.id
        FROM (
            SELECT
                fs.id,
                pt.id as product_tmpl_id
            FROM
                fs_product_image fs,
                product_template pt,
                storage_image si
            WHERE
                fs.x_old_storage_file_id = si.file_id
                AND si.id = pt.x_main_image_id
            ) AS sub
        WHERE
            sub.product_tmpl_id = product_product.product_tmpl_id;
        """
    )
    _logger.info("%s main image linked", cr.rowcount)

    _logger.info("Migrate image_medium for fs_product_image")
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
            'fs.product.image',
            fsi.id,
            'specific_image_medium',
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
          storage_file f,
          fs_product_image fsi,
          storage_image si,
          storage_thumbnail st
        WHERE
          f.id = si.file_id
          AND si.file_id = fsi.x_old_storage_file_id
          AND st.res_model = 'storage.image'
          AND si.id = st.res_id
          AND st.size_x = 128;
        """(
            fs_storage_id,
        )
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

    _logger.info("Migrate image_medium for fs_image")
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
            'fs.image',
            fsi.id,
            'image_medium',
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
            storage_file f,
            fs_image fsi,
            storage_image si,
            storage_thumbnail st
        WHERE
            f.id = si.file_id
            AND si.file_id = fsi.x_old_storage_file_id
            AND st.res_model = 'storage.image'
            AND si.id = st.res_id
            AND size_x = 128;
        """,
        (fs_storage_id,),
    )


def migrate(cr, version):
    migrate_product_media(cr)
    migrate_product_image(cr)
