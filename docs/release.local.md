# Alcyon release process


Workflow for release is slightly different during curent development process.
Specifics are mainly due to the large amount of data involved.


# Release numbering

10.x.y

x = major release where we do a full upgrade of data
y = minor release to fix, add features and can include data diff loads.


# Generating CSV data

When updating data, you need to drag them from DB2 and put them in csv files:

There are 3 types of csv files used:

*Standard*: Full export from db2 converted to Odoo format
*Diff*: Partial changes to play on top of previous version of *Standard*
*Transactional history*: Rarely generated, this is an extract of data in DB2 format
to play with locally.


Configure your importer in docker-compose.yml:

[DB2 option](./db2-options.md)

And generate the csv files:

[Generate CSV files from DB2](./generate_csv_from_db2.md)


# Release with data update

Due to large csv files, to avoid an git history overload,
it makes sense to only update sample data in the PRs.

Full data must be updated only in release creation.
