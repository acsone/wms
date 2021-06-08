odoo.define("web_weighing_widget", function(require) {
  "use strict";

  var form_widgets = require("web.form_widgets");
  var core = require("web.core");
  var session = require("web.session");
  var Model = require("web.Model");

  var WeighingWidget = form_widgets.FieldFloat.extend({
    template: "WebWeighingWidget",

    init: function() {
      this.proxyUrl = null;
      this.status = "FIXED";
      this.weightPoolingIntervalId = null;
      this._super.apply(this, arguments);
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
        const response = await fetch(self.proxyUrl + "/hw_proxy/" + "weight");
        const data = await response.json();
        if (self.view.get("actual_mode") !== "view") {
          self.set_value(data.value);
          self.set_status(data.status);
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

    set_status: function(status) {
      if (this.view.get("actual_mode") !== "view" && !this.get("effective_readonly")) {
        this.status = status;
        const input = this.$el[0];
        let color = "#F16567";
        if (status === "FIXED") {
          color = null;
        }
        input.style.backgroundColor = color;
      }
    },

    is_syntax_valid: function() {
      return this.status === "FIXED";
    },
  });

  core.form_widget_registry.add("weighing_widget", WeighingWidget);

  return {
    WeighingWidget: WeighingWidget,
  };
});
