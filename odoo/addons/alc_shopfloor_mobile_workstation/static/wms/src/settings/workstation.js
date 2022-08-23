/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

import {page_registry} from "/shopfloor_mobile_base/static/wms/src/services/page_registry.js";

const registry_key = "workstation";
const WorkstationBase = page_registry.get(registry_key);

// Override original method to re-route to home instead of settings
WorkstationBase.component.methods.on_scan = function(scanned) {
  this.odoo.call("setdefault", {barcode: scanned.text}).then(result => {
    this.workstation_scanned = true;
    // TODO : See how well a 404 when the shopfloor_workstation
    // module is not installed will be handeled.
    // Maybe there will be some this.$root.appconfig.features.xyz
    // to test if installed.
    this.scan_data = result.data;
    this.scan_message = result.message;
    if (this.scan_data) {
      this.$root.workstation = this.scan_data;
      if (this.scan_data.profile) {
        this.$root.trigger("profile:selected", this.scan_data.profile, true);
      }
      // TODO: the success message will not be displayed, as we change screen !
      this.$root.$router.push({name: "home"});
    }
  });
};
