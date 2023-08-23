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
  line_actions.push({name: "Declare overstock", event_name: "action_overstock"});
  return line_actions;
};

LocationContentTransferBase.component.methods.on_action_overstock = function () {
  let endpoint, endpoint_data;
  const data = this.state.data;
  endpoint = "overstock_line";
  endpoint_data = {
    location_id: data.move_line.location_dest.id,
    move_line_id: data.move_line.id,
  };

  this.wait_call(this.odoo.call(endpoint, endpoint_data));
};
