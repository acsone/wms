/**
 * Copyright 2021 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {process_registry} from "/shopfloor_mobile_base/static/wms/src/services/process_registry.js";

const registry_key = "cluster_picking";
const ClusterPickingBase = process_registry.get(registry_key);

// Keep the pointer to the orginal method
let screen_title_method = ClusterPickingBase.component.methods.screen_title;

ClusterPickingBase.component.methods.screen_title = function () {
  let title = screen_title_method.bind(this)();
  if (_.isEmpty(this.current_batch()) || this.state_is("confirm_start")) return title;
  const release_channel_code = this?.current_picking()?.release_channel?.code;
  if (release_channel_code) {
    title = release_channel_code + " > " + title;
  }
  return title;
};
