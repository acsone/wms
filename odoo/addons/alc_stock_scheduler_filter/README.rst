.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

================
Alc Stock Scheduler Filter
================

This addon improves the functionality of the stock scheduler by introducing
filters that allow for more targeted selection of stock orderpoints during
the scheduling process.

How to test?
------------

- Choose a supplier and specify their managing days.
- When you open the "Run scheduler" action you will see new filters added (by suppliers, by days).
- Apply the supplier filter to only consider orderpoints from the selected suppliers.
- Use the day filter to search for suppliers whose managing days match your selection.
- The system will generate a default orderpoint for any unavailable products
  that lack a configured orderpoint.