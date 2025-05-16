===================================
Alc Stock Location Weight Index Opt
===================================

This module addresses performance bottlenecks during stock picking validation,
particularly in environments with high data volume.

Context and Problems
--------------------

- The ``net_weight`` and ``forecast_weight`` fields on ``stock.location`` are
  computed, non-stored field used only for display purposes in views.
  It depends on ``incoming_move_line_ids`` and ``outgoing_move_line_ids`` which
  impact picking validation.

  For example: during RMA reception pickings, customer
  location is used as source. This location by its nature is linked to a high
  number of move lines.

  When move lines are updated by ``_action_done``, ``_modified_triggers``
  go through these relations to find impacted locations and mark them for
  recomputation.

- The default ``_order`` on ``stock.move.line`` uses ``result_package_id``,
  which forces a join to the ``stock_quant_package`` table in all ordered queries,
  even when packaging is not relevant.

- There is no combined index on ``(location_dest_id, id)`` in ``stock_move_line``,
  which degrades the performance of queries filtered by location and ordered by id.

Solutions
---------

- The compute method is overridden to remove dependencies on move lines,
  avoiding unnecessary recomputations.
- The _order for stock_move_line is simplified.
- A combined index is added on ``stock_move_line(location_dest_id, id)``, improving
  the performance of ordered queries.


**PS: Probably this module should be removed in next migration.**