.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===================================
Alc Shopfloor stock release channel
===================================

This module adds a setting option to shopfloor clustor picking scenario to allow
batch creation restricted to only released pickings. If this option is set to true,
the batch will only select pickings assigned to a release channel an make sure
they all belongs to the same one.
