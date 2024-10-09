===========================================
RMA Sale Stock Restocking Fee Invoicing
===========================================

The `rma_sale_stock_restocking_fee_invoicing` addon extends the functionality
of the `sale_stock_restocking_fee_invoicing` module to handle restocking fees
in Return Merchandise Authorization (RMA) processes.

A new checkbox, `Charge Restocking Fee`, is added to the rma reason model.
If this option is selected and the customer is set to be charged restocking
fees, the corresponding reception move generated from the RMA will be flagged
for restocking fees.

Once the reception is completed, sales order lines for the restocking fee are
automatically added to the sales order, whether the return was initiated
through the delivery order or the sales order.

Configuration
=============

Set Restocking Fees for RMA Reasons:

- Go to RMA > Configuration > RMA Reasons.
- For each reason that should trigger a restocking fee, open the reason and check the box Charge Restocking Fee.

Set Operation to Update Sales Order Line Quantity on Refund:

- Go to RMA > Configuration > RMA Operations.
- Select an operation and set `Action Create Refund` to `Update Quantity`. This will link the reception move to the corresponding sales order line and ensure that the restocking fee is added to the sales order.