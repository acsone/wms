import {ScenarioBaseMixin} from "./mixins.js";
import {process_registry} from "../services/process_registry.js";

export var SinglePackStatesMixin = {
    data: function() {
        return {
            states: {
                // Generic state for when to start w/ scanning a pack or loc
                start: {
                    display_info: {
                        title: "Start by scanning a pack or a location",
                        scan_placeholder: "Scan pack",
                    },
                    enter: () => {
                        this.state_reset_data();
                    },
                    on_scan: scanned => {
                        const data = this.state.data;
                        this.wait_call(
                            this.odoo.call("start", {
                                barcode: scanned.text,
                                confirmation: data.confirmation_required,
                            })
                        );
                    },
                },
                scan_location: {
                    display_info: {
                        title: "Set a location",
                        scan_placeholder: "Scan location",
                        show_cancel_button: true,
                    },
                    on_scan: (scanned, confirmation = false) => {
                        this.state_set_data({location_barcode: scanned.text});
                        this.wait_call(
                            this.odoo.call("validate", {
                                package_level_id: this.state.data.id,
                                location_barcode: scanned.text,
                                confirmation: confirmation,
                            })
                        );
                    },
                    on_cancel: () => {
                        this.wait_call(
                            this.odoo.call("cancel", {
                                package_level_id: this.state.data.id,
                            })
                        );
                    },
                },
            },
        };
    },
};

export var SinglePackTransfer = Vue.component("single-pack-transfer", {
    mixins: [ScenarioBaseMixin, SinglePackStatesMixin],
    template: `
        <Screen :screen_info="screen_info">
            <template v-slot:header>
                <state-display-info :info="state.display_info" v-if="state.display_info"/>
            </template>
            <searchbar v-if="state_is(initial_state_key)" v-on:found="on_scan" :input_placeholder="search_input_placeholder"></searchbar>
            <searchbar v-if="state_is('scan_location')" v-on:found="on_scan" :input_placeholder="search_input_placeholder" :input_data_type="'location'"></searchbar>
            <detail-operation v-if="state.key != 'show_completion_info' && _.result(state, 'data.picking')" :record="state.data" />
            <last-operation v-if="state_is('show_completion_info')" v-on:confirm="state.on_confirm"></last-operation>
            <cancel-button v-on:cancel="on_cancel" v-if="show_cancel_button"></cancel-button>
        </Screen>
    `,
    data: function() {
        return {
            usage: "single_pack_transfer",
            show_reset_button: true,
            initial_state_key: "start",
            states: {
                show_completion_info: {
                    on_confirm: () => {
                        // TODO: turn the cone?
                        this.state_to("start");
                    },
                },
            },
        };
    },
});
process_registry.add("single_pack_transfer", SinglePackTransfer, {
    demo_src: "demo/demo.single_pack_transfer.js",
});
