/** @odoo-module **/

import {COMMANDS} from "@barcodes/barcode_handlers";

function clickOnButton(selector) {
  const button = document.body.querySelector(selector);
  if (button) {
    button.click();
  }
}

COMMANDS["O-CMD.MAIN-MENU"] = () => clickOnButton(".goto-barcode-app");
COMMANDS["O-CMD.CANCEL"] = () => clickOnButton(".o_form_button_cancel");
