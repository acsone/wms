odoo.define('specific_account.reconciliation_custom', function (require) {
    "use strict";

    var core = require('web.core');
    var _t = core._t;
    var FieldMany2One = core.form_widget_registry.get('many2one');
    var reconciliation = require('account.reconciliation');

    reconciliation.bankStatementReconciliationLine.include({

        /*
         * Overrides the parent method to remove parent_id=false from the domain.
         * See parent method in account/static/src/js/account_reconciliation_widgets.js#L1760
         */
        createFormWidgets: function() {
            var self = this;
            // We don't want to call the parent method, only the parent parent one.
            // Else the partner selector field is added twice.
            reconciliation.abstractReconciliationLine.prototype.createFormWidgets.apply(this, arguments);

            // generate the change partner "form"
            var change_partner_field = {
                relation: "res.partner",
                string: _t("Partner"),
                type: "many2one",
                domain: [['parent_id', '=', false]],
                help: "",
                readonly: false,
                required: true,
                selectable: true,
                states: {},
                views: {},
                context: {},
            };
            var change_partner_node = {
                tag: "field",
                children: [],
                required: true,
                attrs: {
                    invisible: "False",
                    modifiers: '',
                    name: "change_partner",
                    nolabel: "True",
                }
            };
            self.field_manager.fields_view.fields["change_partner"] = change_partner_field;
            self.change_partner_field = new FieldMany2One(self.field_manager, change_partner_node);
            self.change_partner_field.appendTo(self.$(".change_partner_container"));
            self.change_partner_field.on("change:value", self.change_partner_field, function() {
                self.changePartner(this.get_value());
            });
            self.change_partner_field.$el.find("input").attr("placeholder", self.st_line.communication_partner_name || _t("Select Partner"));
        },

    });

});
