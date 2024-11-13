=============================
ACCOUNT MOVE RECONCILE SEARCH
=============================

This module enhances the search in the reconciliation view of account
move lines by optimizing the search behavior and improving performance:

- **Removed Search on Partner:** The search for the partner is removed when users
  search using the move name. Combining the partner search with the name search in
  large datasets is inefficient, as the partner search also triggers searches on
  associated fields like email, address, and others, which adds unnecessary overhead.

- **Removed Search on amount_residual:** The amount_residual search filter is removed from the
  search view when searching with the move name. While it is unclear why Odoo
  included this, it proves inefficient in most cases, as users typically search for
  the account move name or ref, not the residual amount. If needed, users can filter
  specifically with the amount fields

- **Added Trigram Index on `name` and `ref` Fields:** A trigram index is added to
  the `name` and `ref` fields, significantly improving the search performance for
  these fields, especially when using partial string matching or LIKE queries.

- **Removed Unaccent Search on `name` and `ref`:** The unaccented search on `name`
  and `ref` has been removed to improve search efficiency. Unaccented searches are
  slower and are unnecessary for this case since the move name and reference are
  typically used with exact matches in reconciliations.
