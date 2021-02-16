#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from datetime import datetime
from os import listdir
from os.path import isfile, join
from StringIO import StringIO

import click
import click_odoo
import numpy as np
import pandas as pd
import psycopg2


# pylint: disable=unnecessary-lambda,no-value-for-parameter
def dataframe_to_sql_table(env, dataframe, verbose):
    # Create temporary DF table for products
    # NB : index is just to stick to the DF, first column is the index
    env.cr.execute(
        """ CREATE TEMPORARY TABLE
                        dataframe_table (
                            index INTEGER,
                            "Date-Time" VARCHAR,
                            Description VARCHAR,
                            "Dim Unit" VARCHAR,
                            "Dim Wgt" NUMERIC,
                            Factor NUMERIC,
                            Height NUMERIC,
                            Length NUMERIC,
                            Ref VARCHAR,
                            Secondary VARCHAR,
                            Sequence NUMERIC,
                            "Site ID" VARCHAR,
                            SnapShotFile VARCHAR,
                            Updated BOOLEAN,
                            User1 NUMERIC,
                            User2 NUMERIC,
                            User3 NUMERIC,
                            User4 VARCHAR,
                            User5 VARCHAR,
                            User6 VARCHAR,
                            User7 VARCHAR,
                            User8 VARCHAR,
                            "Vol Unit" VARCHAR,
                            Volume NUMERIC,
                            Weight NUMERIC,
                            "Wgt Unit" VARCHAR,
                            Width NUMERIC,
                            Secondary_id INTEGER)
                    """
    )
    if verbose:
        click.echo("dataframe temporary table created. . .")
        click.echo("Dropping DataFrame into a buffer . . .")

    if verbose:
        click.echo("dataframe {}. . .".format(dataframe.head()))

    buffer = StringIO()
    dataframe.to_csv(buffer, index_label="id", header=False)
    buffer.seek(0)

    try:
        env.cr.copy_from(buffer, "dataframe_table", sep=",")
        env.cr.commit()
        if verbose:
            click.echo("Trying to copy DataFrame to temporary table. . .")
    except (Exception, psycopg2.DatabaseError) as error:
        env.cr.rollback()
        logging.getLogger(__name__).error(
            "Error when trying to to copy dataframe into temporary table %s", error
        )
        return 1

    if verbose:
        click.echo("I tried,  it went well!. . .")
    return None


def format_files_to_dataframe(env, path_to_files, verbose):
    # list all files in one dataframe
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f))]
    all_data = pd.DataFrame()
    # new_export = pd.DataFrame()
    # concat all files in one DF
    for file in files:
        if verbose:
            click.echo("Start processing file: {}. . .".format(file))

        df = pd.read_excel(path_to_files + file)

        # Name 'primary' is ambiguous when using sql tables. cf primary key ... so renaming it into the df
        # NB: sometimes we have Ref in the xlsx sheets => using this for consistancy
        if "Primary" in df.columns:
            df.rename(columns={"Primary": "REF "}, inplace=True)
        # Sometimes Weight, sometimes Poids... just using weight all the time for consistancy
        if "Poids" in df.columns:
            df.rename(columns={"Poids": "Weight"}, inplace=True)
        # df['file name'] = file
        all_data = all_data.append(df, ignore_index=True, sort=True)
        # new_export = new_export.append(df, ignore_index=True, sort=True)

    # Replace Nan values with proper value for consistancy in the SQL table
    # Fill withe spaces with NaN to convert it to zeros after
    all_data["User1"] = all_data["User1"].replace(r"^\s*$", np.nan, regex=True)

    all_data = all_data.fillna(
        value={
            "Description": "",
            "REF ": 0,
            "Weight": 0,
            "Dim Wgt": 0,
            "Factor": 0,
            "User1": 0,
            "User2": 0,
            "User3": 0,
            "Sequence": 0,
            "Secondary": "",
            "Updated": False,
            "Volume": 0,
        }
    )

    all_data["REF "] = all_data["REF "].astype(np.int64)
    all_data["REF "] = all_data["REF "].apply(lambda x: "{:0>7}".format(x))
    all_data["REF "] = all_data["REF "].astype(str)
    # REF is 7 char min. zeros were removed at the beginning because of np.int6' -- which is necessary
    # to prevent pandas to interpret those ref as float and then put a .0 at the end

    all_data["User1"] = all_data["User1"].astype(np.int64)
    all_data["User2"] = all_data["User2"].astype(np.int64)
    all_data["User2"] = all_data["User2"].apply(lambda x: "{:0>7}".format(x))
    all_data["User3"] = all_data["User3"].astype(np.int64)

    if verbose:
        click.echo("Dataframe Columns : {}. . .".format(all_data.columns))
        click.echo("Dataframe Head : {}. . .".format(all_data.head()))
        click.echo("Dataframe types: {}".format(all_data.dtypes))
    return all_data


def split_products_and_packagings(env, all_data_dataframe, verbose):

    no_package_info = all_data_dataframe[all_data_dataframe["Secondary"] == ""]
    if verbose:
        click.echo("no package info df: {}. . .".format(no_package_info.head()))

    # Extract product related DF
    product_data = all_data_dataframe[all_data_dataframe["Secondary"] == "PIECE"]
    product_data = product_data.append(no_package_info, ignore_index=True, sort=True)

    if verbose:
        click.echo("products data: {}. . .".format(product_data.head()))

    # Concat all_data with product_data + drop_duplicates ==> keep only packaging related data
    product_packaging_data = pd.concat(
        [all_data_dataframe, product_data, product_data]
    ).drop_duplicates(keep=False)
    # Maps packaging type on Odoo packaging type ids
    PACKAGING_TYPES = {
        "CARTON": env.ref("alc_product_packaging.product_packaging_type_box").id,
        "FARDELAGE": env.ref(
            "alc_product_packaging.product_packaging_type_shrink_wrap"
        ).id,
        "PALETTE": env.ref("alc_product_packaging.product_packaging_type_palette").id,
    }

    # Clean ids : default pandas format is float : fill  NaN with zero then enforce INT type
    product_packaging_data["Secondary_id"] = (
        product_packaging_data["Secondary"].map(PACKAGING_TYPES).astype(int)
    )

    product_data[
        "Secondary_id"
    ] = 0  # Fill with zero for product to always drop in the same sql table

    # Drop all products and packagings that are duplicated
    product_data.drop_duplicates(inplace=True)
    product_packaging_data.drop_duplicates(inplace=True)

    product_data["REF "] = product_data["REF "].astype(str)
    product_data["User1"] = product_data["User1"].astype(np.int64)
    product_data["User2"] = product_data["User2"].astype(np.int64)
    product_data["User2"] = product_data["User2"].apply(lambda x: "{:0>7}".format(x))
    product_data["User3"] = product_data["User3"].astype(np.int64)

    product_packaging_data["REF "] = product_packaging_data["REF "].astype(str)
    product_packaging_data["User1"] = product_packaging_data["User1"].astype(np.int64)
    product_packaging_data["User2"] = product_packaging_data["User2"].astype(np.int64)
    product_packaging_data["User2"] = product_packaging_data["User2"].apply(
        lambda x: "{:0>7}".format(x)
    )
    product_packaging_data["User3"] = product_packaging_data["User3"].astype(np.int64)

    return product_data, product_packaging_data


def update_products_table(env, data, verbose):
    # cleanup data
    env.cr.execute(
        """
         UPDATE
            product_product pp
         SET
            weight = null,
            height = null,
            width = null,
            length = null
    """
    )
    # Working on the product
    # Put DF to sql temporary table
    dataframe_to_sql_table(env, data, verbose)

    # Check all products in the dataframe exist in Odoo
    env.cr.execute(
        """ SELECT Ref, Description
                       FROM dataframe_table p_df
                       WHERE p_df.Ref NOT IN (SELECT pt.default_code FROM product_template pt)
    """
    )
    result = env.cr.fetchall()
    if result:
        click.echo(
            "Attention! Some products are in the excel sheets but not in the Odoo database : {}. . .".format(
                result[0]
            )
        )

    if verbose:
        click.echo("Updating Products table. . .")

    # Look for no barcode
    env.cr.execute(
        """ SELECT Count(User1)
                FROM dataframe_table
                WHERE  User1 = 0
    """
    )
    result = env.cr.fetchall()
    if verbose:
        click.echo("no barcode {}. . .".format(result))

    # Look for no cnk
    env.cr.execute(
        """ SELECT Count(User2)
                FROM dataframe_table
                WHERE  User2 = 0
    """
    )
    result = env.cr.fetchall()
    if verbose:
        click.echo("no ucnk {}. . .".format(result))

    # Look for duplicates barcode
    env.cr.execute(
        """ SELECT Ref, User1
                FROM dataframe_table
                WHERE  User1 != 0 AND User1 IN (SELECT User1 FROM dataframe_table GROUP BY User1 Having COUNT(*) >1)
    """
    )
    result = env.cr.fetchall()
    products_refs = tuple([str(elt[0]) for elt in result])
    if verbose:
        click.echo("duplicated barcode {}, count: {}. . .".format(result, len(result)))
        click.echo("products_refs {},. . .".format(products_refs))

    env.cr.execute(
        """ DELETE FROM dataframe_table
                WHERE Ref IN %(products_refs)s
    """,
        {"products_refs": products_refs},
    )
    env.cr.commit()
    # Look for duplicates cnk
    env.cr.execute(
        """ SELECT Ref, User2
                FROM dataframe_table
                WHERE  User2 != 0 AND User2 IN (SELECT User2 FROM dataframe_table GROUP BY User2 Having COUNT(*) >1)
    """
    )
    result2 = env.cr.fetchall()
    products_refs = tuple([elt[0] for elt in result2])
    if verbose:
        click.echo("duplicated cnk {}, count: {}. . .".format(result2, len(result2)))

    env.cr.execute(
        """ DELETE FROM dataframe_table
                WHERE Ref IN %(products_refs)s
    """,
        {"products_refs": products_refs},
    )
    env.cr.commit()

    env.cr.execute(
        """ UPDATE
                            product_product pp
                       SET
                            weight = p_df.Weight,
                            height = p_df.Height,
                            width = p_df.Width,
                            length = p_df.Length
                       FROM dataframe_table p_df
                       WHERE pp.default_code = p_df.Ref
                """
    )

    env.cr.commit()
    env.cr.execute(
        """ UPDATE
                            product_product pp
                       SET
                            barcode = p_df.User1
                       FROM dataframe_table p_df
                       WHERE p_df.User1 != 0 AND pp.default_code = p_df.Ref
                """
    )
    env.cr.commit()

    if verbose:
        click.echo(
            "I updated your products with the dataframe table infos. Now dropping the temporary table for products. . ."
        )

    # Drop temporary table
    env.cr.execute("""DROP TABLE dataframe_table""")


def update_product_packagings_table(env, data, verbose):
    # Working on the product packaging
    # Put DF to sql temporary table

    # Data in mm for packagings : conversion for now
    data["Height"] = data["Height"] * 10
    data["Width"] = data["Width"] * 10
    data["Length"] = data["Length"] * 10

    dataframe_to_sql_table(env, data, verbose)

    if verbose:
        click.echo("Creating indexes to speed up product packagings deletion. . .")

    # env.cr.execute("""CREATE INDEX idx1 ON purchase_order_line (product_packaging) """)
    # env.cr.commit()
    # env.cr.execute("""CREATE INDEX idx2 ON sale_order_line (product_packaging) """)
    # env.cr.commit()
    # env.cr.execute("""CREATE INDEX idx3 ON stock_move (product_packaging) """)
    # env.cr.commit()
    # # env.cr.execute(
    # #     """CREATE INDEX idx4 ON stock_quant_package (product_packaging_id) """
    # # )
    # # env.cr.commit()
    # env.cr.execute("""CREATE INDEX idx5 ON stock_quant_package (packaging_id) """)
    # env.cr.commit()
    # env.cr.execute("""CREATE INDEX idx6 ON stock_quant (packaging_type_id) """)
    # env.cr.commit()

    if verbose:
        click.echo("Deleting all packagings for products. . .")

    start = datetime.now()
    env.cr.execute("""DELETE FROM product_packaging """)
    end = datetime.now()
    delta = end - start
    seconds = delta.seconds

    if verbose:
        click.echo("Dropping indexes on product packagings. . .")

    env.cr.execute("""DROP INDEX idx1""")
    env.cr.commit()
    env.cr.execute("""DROP INDEX idx2""")
    env.cr.commit()
    env.cr.execute("""DROP INDEX idx3""")
    env.cr.commit()
    # env.cr.execute("""DROP INDEX idx4""")
    # env.cr.commit()
    env.cr.execute("""DROP INDEX idx5""")
    env.cr.commit()
    env.cr.execute("""DROP INDEX idx6""")
    env.cr.commit()

    if verbose:
        click.echo(
            "Time needed to delete existing packagings: {} hours and {} minutes. . .".format(
                seconds // 3600.0, (seconds // 60.0) % 60.0
            )
        )
        click.echo("Creating packagings for products based on input file. . .")

    # Create product packaging
    start = datetime.now()
    env.cr.execute(
        """ INSERT INTO product_packaging
                            (name,
                            packaging_type_id,
                            max_weight,
                            height,
                            height_cm,
                            width,
                            width_cm,
                            lngth,
                            length_cm,
                            product_tmpl_id,
                            barcode,
                            qty)
                    SELECT
                        p_df.Secondary,
                        p_df.Secondary_id,
                        p_df.Weight,
                        p_df.Height,
                        p_df.Height / 10,
                        p_df.Width,
                        p_df.Width / 10,
                        p_df.Length,
                        p_df.Length / 10,
                        pt.id,
                        p_df.User1,
                        p_df.User3
                    FROM dataframe_table p_df
                    JOIN product_template pt ON p_df.Ref = pt.default_code
    """
    )

    env.cr.commit()
    end = datetime.now()
    delta = end - start
    seconds = delta.seconds
    if verbose:
        click.echo(
            "Time needed to import packagings: {} hours and {} minutes. . .".format(
                seconds // 3600.0, (seconds // 60.0) % 60.0
            )
        )

    # if verbose:
    #     click.echo("Updating filters on missing dimensions. . .")

    # start = datetime.now()
    # env["product.template"].search([])._compute_has_no_dimensions()
    # env["product.template"].search([])._compute_packaging_has_no_dimensions()

    # end = datetime.now()
    # delta = end - start
    # seconds = delta.seconds

    # if verbose:
    #     click.echo(
    #         "Time needed to update filters: {} hours and {} minutes. . .".format(
    #             seconds // 3600.0, (seconds // 60.0) % 60.0
    #         )
    #     )

    if verbose:
        click.echo("Dropping packaging product temporary table. . .")
    # Drop temporary table
    env.cr.execute("""DROP TABLE dataframe_table""")


@click.command()
@click.option(
    "--path-to-files", required=True, help="Directory where the xlsx files are."
)
@click.option("--verbose", default=False, help="Helps you with short messages.")
@click_odoo.env_options(default_log_level="info")
def main(env, path_to_files, verbose):
    if True and verbose:
        click.echo("Start processing xlsx files. . .")

    # Format and split input data
    all_data = format_files_to_dataframe(env, path_to_files, verbose)
    product_data, product_packaging_data = split_products_and_packagings(
        env, all_data, verbose
    )

    update_products_table(env, product_data, verbose)
    update_product_packagings_table(env, product_packaging_data, verbose)


if __name__ == "__main__":
    main()
