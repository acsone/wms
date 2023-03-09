=============================
Alc Sale Processing Finalizer
=============================

This addon allows to automatically close a Sale older than 3 months unless it's
linked to a long term delivery carrier. By closing a sale we mean canceling
quantities not yet delivered.

Test
====
To ease your test you may need
 * to add the Sales Management module
 * to put the date of your PC more than 3 months in the past to create the SO
 * or to put the date of your PC more than 3 months in the future to run the
   scheduled task

Create an SO and confirm it. If you don't have set the automatic lock of
confirmed sales in settings then lock the SO manually.
Run the scheduled task called 'Cancel Sales BO > 3months'

