/** @odoo-module **/

import {registry} from "@web/core/registry";
import {session} from "@web/session";
import {useService} from "@web/core/utils/hooks";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
const {Component, onWillUnmount, onWillStart, onMounted, onError, useState} = owl;

export class WebScale extends Component {
  setup() {
    this.proxyUrl = null;
    this.weightPoolingIntervalId = null;
    this.error_notification = null;
    this.orm = useService("orm");
    this.state = useState({
      value: 0,
      status: "FIXED",
      error: null,
      inputColor: "transparent",
    });

    onWillStart(async () => {
      await this.setProxyUrl();
    });

    onMounted(() => {
      this.start_weight_pooling();
    });

    onError(() => {
      this.stop_weight_pooling();
    });
    onWillUnmount(() => {
      this.stop_weight_pooling();
    });
  }

  async getUserData() {
    return await this.orm.call("res.users", "read", [session.uid], {
      fields: ["pywebdriver_proxy_ip"],
    });
  }

  async setProxyUrl() {
    const userData = await this.getUserData();
    if (userData.length === 1) {
      this.proxyUrl = `${userData[0].pywebdriver_proxy_ip}/hw_proxy/weight`;
    } else {
      this.proxyUrl = "";
    }

    this.on_mode_change();
  }

  start_weight_pooling() {
    const self = this;
    this.stop_weight_pooling();
    this.weightPoolingIntervalId = setInterval(async () => {
      try {
        const response = await fetch(self.proxyUrl);
        const data = await response.json();
        self.set_weighing_data(data);
      } catch (error) {
        self.on_connection_error(this.env._t("Trying to reconnect..."));
      }
    }, 500);
  }

  stop_weight_pooling() {
    if (this.weightPoolingIntervalId) {
      clearInterval(this.weightPoolingIntervalId);
      this.weightPoolingIntervalId = null;
    }
  }

  on_mode_change() {
    if (this.env.model.root.mode === "edit") {
      this.start_weight_pooling();
    } else {
      this.stop_weight_pooling();
    }
  }

  set_weighing_data(data) {
    if (this.env.model.root.mode === "edit") {
      if (data.status === "ERROR") {
        // Status change to error...
        // notify user.
        this.on_connection_error(data.value);
      } else {
        if (this.state.status !== "ERROR") {
          this.on_connection_fixed();
        }
        this.props.update(data.value);
      }
      this.set_status(data.status);
    }
  }

  on_connection_error(message) {
    this.state.error =
      this.env._t("Could not connect to weighing machine") + ": " + message;
    this.error_notification = true;
  }

  on_connection_fixed() {
    if (this.error_notification) {
      this.state.error = null;
      this.error_notification = false;
    }
  }

  set_status(status) {
    if (this.env.model.root.mode === "edit") {
      this.state.status = status;
      let color = "#F16567";
      if (!status || status === "FIXED" || status === "ERROR") {
        color = "transparent";
      }
      this.state.inputColor = color;
    }
  }
}
WebScale.props = {
  ...standardFieldProps,
};
WebScale.template = "WebScale";

registry.category("fields").add("web_scale", WebScale);
