/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "location_content_transfer";
const LocationContentTransferBase = process_registry.get(registry_key);

// Keep the pointer to the orginal method
const actions_method = LocationContentTransferBase.component.methods.line_actions;

LocationContentTransferBase.component.methods.line_actions = function () {
  const line_actions = actions_method.bind(this)();
  line_actions.push({name: "Print label", event_name: "action_print_label"});
  return line_actions;
};

LocationContentTransferBase.component.methods.on_action_print_label = function () {
  var endpoint, endpoint_data;
  const data = this.state.data;
  endpoint = "print_label";
  endpoint_data = {
    location_id: data.operation.location_src.id,
    operation_id: data.operation.id,
  };
  if (data.operation.type === "lot") {
    endpoint_data.lot_id = data.operation.lot.id;
  }
  this.wait_call(this.odoo.call(endpoint, endpoint_data));
};
