# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Create fs_product_brand_image records from storage_file")
    cr.execute(
        """
            INSERT INTO  fs_product_brand_image (
                brand_id,
                sequence,
                write_uid,
                write_date,
                create_uid,
                create_date,
                name,
                mimetype
            )
            SELECT
                pb.id,
                0,
                f.write_uid,
                f.write_date,
                f.create_uid,
                f.create_date,
                f.name,
                f.mimetype
            FROM
                product_brand as pb,
                storage_image as s,
                storage_file as f
            WHERE
                pb.x_image_id = s.id
                AND s.file_id = f.id;
    """
    )
    _logger.info("%s fs_product_rand_image records created", cr.rowcount)

    cr.execute("select id from fs_storage where code = 'fsprd_eshop'")
    fs_storage_id = cr.fetchone()[0]
    _logger.info(
        "Create ir_attachment records from storage_file linked to one product_brand"
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
                concat(f.name, '.png'),
                'binary',
                'fs.product.brand.image',
                fs_product_brand_image.id,
                'specific_image',
                f.create_uid,
                f.create_date,
                f.write_uid,
                f.write_date,
                concat('fsprd_eshop://', f.slug),
                'image/png',
                f.file_size,
                f.checksum,
                %s,
                f.url,
                'fsprd_eshop',
                f.slug
            FROM
                storage_image as s,
                storage_file as f,
                fs_product_brand_image,
                product_brand as pb
            WHERE
                fs_product_brand_image.brand_id = pb.id
                AND pb.x_image_id = s.id
                AND fs_product_brand_image.image_id is null
                AND s.file_id = f.id
    """,
        (fs_storage_id,),
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)

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
            concat(f.name, '.png'),
            'binary',
            'fs.product.brand.image',
            fsi.id,
            'specific_image_medium',
            f.create_uid,
            f.create_date,
            f.write_uid,
            f.write_date,
            concat('fsprd_eshop://', f.slug),
            'image/png',
            f.file_size,
            f.checksum,
            %s,
            f.url,
            'fsprd_eshop',
            f.slug
        FROM
          storage_file f,
          fs_product_brand_image fsi,
          storage_image si,
          storage_thumbnail st,
          product_brand pb
        WHERE
          f.id = si.file_id
          AND pb.x_image_id = si.id
          AND fsi.brand_id = pb.id
          AND st.res_model = 'storage.image'
          AND si.id = st.res_id
          AND st.size_x = 128;
        """(
            fs_storage_id,
        )
    )

    _logger.info("%s ir_attachment records created", cr.rowcount)
