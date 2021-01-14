odoo.define("specific_account.reconciliation_custom", function(require) {
  "use strict";

  var reconciliation = require("account.reconciliation");

  reconciliation.bankStatementReconciliationLine.include({
    /*
     * Overrides the parent method to remove domain filters on customer/supplier flags.
     * See parent method in account/static/src/js/account_reconciliation_widgets.js#L1760
     */
    createFormWidgets: function() {
      this._super();
      this.change_partner_field.field.domain = [["parent_id", "=", false]];
    },
  });
});
