odoo.define("web_weighing_widget", function(require) {
  "use strict";

  const form_widgets = require("web.form_widgets");
  const core = require("web.core");
  const session = require("web.session");
  const Model = require("web.Model");
  const _t = core._t;

  const WeighingWidget = form_widgets.FieldFloat.extend({
    template: "WebWeighingWidget",

    init: function() {
      this.proxyUrl = null;
      this.status = "FIXED";
      this.weightPoolingIntervalId = null;
      this._super.apply(this, arguments);
      this.error_notification = null;
    },

    initialize_content: function() {
      this.$input = undefined;
      this.$error = undefined;
      if (!this.get("effective_readonly")) {
        this.$input = this.$("input");
        this.$error = this.$("#weighing-widget-error");
      }
      this._super();
    },

    start: function() {
      const self = this;
      this.view.on("change:actual_mode", this, this.on_mode_change);
      return $.when(this._super())
        .then(() => {
          new Model("res.users")
            .call("read", [[session.uid], ["pywebdriver_proxy_ip"]])
            .done(result => {
              const data = result[0];
              self.proxyUrl = data.pywebdriver_proxy_ip;
            });
        })
        .then(() => {
          self.on_mode_change();
        });
    },

    start_weight_pooling: function() {
      const self = this;
      this.weightPoolingIntervalId = setInterval(async function() {
        try {
          const response = await fetch(self.proxyUrl + "/hw_proxy/weight");
          const data = await response.json();
          self.set_weighing_data(data);
        } catch (error) {
          self.on_connection_error(_t("Trying to reconnect..."));
        }
      }, 500);
    },

    stop_weight_pooling: function() {
      if (this.weightPoolingIntervalId) {
        clearInterval(this.weightPoolingIntervalId);
      }
    },

    on_mode_change: function() {
      if (this.view.get("actual_mode") === "edit" && !this.get("effective_readonly")) {
        this.start_weight_pooling();
      } else {
        this.stop_weight_pooling();
      }
    },

    set_weighing_data: function(data) {
      if (this.view.get("actual_mode") !== "view") {
        if (data.status === "ERROR") {
          // Status change to error...
          // notify user.
          this.on_connection_error(data.value);
        } else {
          if (this.status !== "ERROR") {
            this.on_connection_fixed();
          }
          this.set_value(data.value);
        }

        this.set_status(data.status);
      }
    },

    on_connection_error: function(message) {
      this.$error.get(0).title =
        _t("Could not connect to weighing machine") + ": " + message;
      this.$error.show();
      this.error_notification = true;
    },

    on_connection_fixed: function() {
      if (this.error_notification) {
        this.$error.get(0).title = "";
        this.$error.hide();
        this.do_notify(
          _t("Connection restored"),
          _t("Connection to weighing machine restored"),
          false
        );
        this.error_notification = false;
      }
    },

    set_status: function(status) {
      if (this.view.get("actual_mode") !== "view" && !this.get("effective_readonly")) {
        this.status = status;
        let color = "#F16567";
        if (!status || status === "FIXED" || status === "ERROR") {
          color = "transparent";
        }
        this.$input.css("background-color", color);
      }
    },

    is_syntax_valid: function() {
      const res = this._super();
      return res && (!this.status || this.status !== "ACQUIRING");
    },
  });

  core.form_widget_registry.add("weighing_widget", WeighingWidget);

  return {
    WeighingWidget: WeighingWidget,
  };
});
