/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "location_content_transfer";
const LocationContentTransferBase = process_registry.get(registry_key);

let template = LocationContentTransferBase.component.template;
LocationContentTransferBase.component.template = template.replace(
  "</Screen>",
  `
    <get-work
    v-if="state_is('start')"
    v-on:get_work="state.on_get_work"
    v-on:manual_selection="state.on_manual_selection"
    />

 </Screen>
 `
);
// Keep the pointer to the orginal method
let data_result_method = LocationContentTransferBase.component.data;
let data = function() {
  // we must bin the original method to this to put it into
  // the object context
  let result = data_result_method.bind(this)();
  // update states for init and start
  // init will get the "get work" screen if no work is started for the current user
  // if we click on "get work", we retrieve some refill to do
  result.states.init = {
    enter: () => {
      this.wait_call(this.odoo.call("start_or_recover"));
    },
  };
  result.states.start = {
    on_get_work: evt => {
      this.wait_call(this.odoo.call("get_work"));
    },
    on_manual_selection: evt => {
      this.state_to("scan_location");
    },
  };
  return result;
};
LocationContentTransferBase.component.data = data;
