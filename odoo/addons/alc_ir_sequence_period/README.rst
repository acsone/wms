.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
IR Sequence Period
==================

This addon make sure that ir_sequence_period scope is covered by STD.

To configure ALCYON fiscal year, you need to create:

* date range type with this values
    * Autogeneration Count: 1
    * Autogeneration Unit: years
    * Duration: 1
    * Unit of time: years
    * Range name expression: ``'%s/%s' % (date_start.strftime('%Y'), date_end.strftime('%Y'))``
* first fiscal year with the preferable start and end dates

The scheduled action 'Auto-generate date ranges' will use the first fiscal
year to calculate the next period's start date and the date range type
to determine the end date and name.

This module also overrides the way Odoo manages invoice sequences by:

- linking the journal to a dedicated sequence for invoices and refunds
- starting the sequence range at the end of the company's fiscal year + 1
- using the end date of the range to obtain the invoice number
- not assigning a sequence number to draft invoices
