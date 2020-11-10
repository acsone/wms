#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from os import listdir
from os.path import isfile, join
from StringIO import StringIO

import psycopg2

import click
import click_odoo
import pandas as pd


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
                            User1 VARCHAR,
                            User2 VARCHAR,
                            User3 VARCHAR,
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
            "Error when trying to to copy dataframe into temporary table %s" % error
        )
        return 1

    if verbose:
        click.echo("I tried,  it went well!. . .")


def format_files_to_dataframe(env, path_to_files, verbose):
    # list all files in one dataframe
    files = [f for f in listdir(path_to_files) if isfile(join(path_to_files, f))]
    all_data = pd.DataFrame()

    # concat all files in one DF
    for file in files:
        df = pd.read_excel(path_to_files + file)
        # Name 'primary' is ambiguous when using sql tables. cf primary key ... so renaming it into the df
        # NB: sometimes we have Ref in the xlsx sheets => using this for consistancy
        if "Primary" in df.columns:
            df.rename(columns={"Primary": "Ref"}, inplace=True)
        # Sometimes Weight, sometimes Poids... just using weight all the time for consistancy
        if "Poids" in df.columns:
            df.rename(columns={"Poids": "Weight"}, inplace=True)

        all_data = all_data.append(df, ignore_index=True, sort=True)

    # Replace Nan values with proper value for consistancy in the SQL table
    all_data = all_data.fillna(
        value={
            "Description": "",
            "Weight": 0,
            "User1": "",
            "User2": "",
            "User3": "",
            "User4": "",
            "User5": "",
            "User6": "",
            "User7": "",
            "User8": "",
            "Dim Wgt": 0,
            "Factor": 0,
            "Sequence": 0,
            "Secondary": "",
            "Updated": False,
            "Volume": 0,
        }
    )

    if verbose:
        click.echo("Dataframe Columns : {}. . .".format(all_data.columns))
        click.echo("Dataframe Head : {}. . .".format(all_data.head()))

    return all_data


def split_products_and_packagings(env, all_data_dataframe, verbose):

    # Extract product related DF
    product_data = all_data_dataframe[all_data_dataframe["Secondary"] == "PIECE"]
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
        product_packaging_data["Secondary"].map(PACKAGING_TYPES).fillna(0).astype(int)
    )
    if verbose:
        click.echo(
            "IDS for packagings: {}. . .".format(product_packaging_data["Secondary_id"])
        )

    product_data[
        "Secondary_id"
    ] = 0  # Fill with zero for product to always drop in the same sql table

    if verbose:
        click.echo(
            "IDS for product -- should always be zero: {}. . .".format(
                product_data["Secondary_id"]
            )
        )

    return product_data, product_packaging_data


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

    # Working on the product
    # Put DF to sql temporary table
    dataframe_to_sql_table(env, product_data, verbose)

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
    # Update my products table
    env.cr.execute(
        """ UPDATE
                            product_template pt
                       SET
                            weight = p_df.Weight,
                            depth = p_df.Height,
                            width = p_df.Width,
                            length = p_df.Length,
                            volume = p_df.Volume
                       FROM dataframe_table p_df
                       WHERE pt.default_code = p_df.Ref
                """
    )
    env.cr.commit()
    if verbose:
        click.echo(
            "I updated your products with the dataframe table infos. Now dropping the temporary table for products. . ."
        )

    # Drop temporary table
    env.cr.execute("""DROP TABLE dataframe_table""")

    # Working on the product packaging
    # Put DF to sql temporary table
    dataframe_to_sql_table(env, product_packaging_data, verbose)
    if verbose:
        click.echo("Updating or creating packagings for products. . .")
    # List all products that does not have packaging and are in the dataframe : create packaging for those one
    env.cr.execute(
        """ SELECT id, default_code, name
                        FROM product_template pt
                        JOIN dataframe_table p_df ON pt.default_code = p_df.Ref
                        WHERE pt.id NOT IN (SELECT product_tmpl_id FROM product_packaging)
                        """
    )
    result = env.cr.fetchall()
    if result:
        product_ids = tuple([r[0] for r in result])
        if verbose:
            click.echo("ids to create: {}. . .".format(product_ids))
        # Create product packaging
        env.cr.execute(
            """ INSERT INTO product_packaging (name, packaging_type_id, max_weight, height, width, lngth, product_tmpl_id)
                            SELECT p_df.Secondary, p_df.Secondary_id, p_df.Weight, p_df.Height, p_df.Width, p_df.Length, pt.id
                            FROM dataframe_table p_df JOIN product_template pt ON p_df.Ref = pt.default_code
                            WHERE pt.id IN %(ids)s
        """,
            {"ids": product_ids},
        )

    if verbose:
        click.echo("Now updating existing packaging product ids. . .")
    # Update my product packaging table
    env.cr.execute(
        """ UPDATE
                            product_packaging p_pckg
                       SET
                            max_weight = p_df.Weight,
                            height = p_df.Height,
                            width = p_df.Width,
                            lngth = p_df.Length
                       FROM (dataframe_table p_df JOIN product_template pt ON p_df.Ref = pt.default_code)
                       WHERE pt.id = p_pckg.product_tmpl_id AND p_pckg.packaging_type_id = p_df.Secondary_id
                   """
    )
    env.cr.commit()

    if verbose:
        click.echo("Dropping packaging product temporary table. . .")
    # Drop temporary table
    env.cr.execute("""DROP TABLE dataframe_table""")


if __name__ == "__main__":
    main()
