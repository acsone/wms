import {ScenarioBaseMixin, GenericStatesMixin} from "./mixins.js";

export var ClusterPicking = Vue.component('cluster-picking', {
    mixins: [ScenarioBaseMixin, GenericStatesMixin],
    template: `
        <Screen :title="menuItem.name">
            <!-- FOR DEBUG -->
            <!-- {{ current_state_key }} -->
            <user-information
                v-if="!need_confirmation && user_notification.message"
                v-bind:info="user_notification"
                />
            <get-work
                v-if="state_is(initial_state_key)"
                v-on:get_work="state.on_get_work"
                v-on:manual_selection="state.on_manual_selection"
                />
            <batch-picking-detail
                v-if="state_is('confirm_start')"
                :info="state.data"
                v-on:confirm="state.on_confirm"
                v-on:cancel="state.on_cancel"
                />
            <batch-picking-line-detail
                v-if="state_in(['start_line', 'scan_destination'])"
                :line="erp_data.data['start_line']"
                />
            <searchbar
                v-if="state_in(['start_line', 'unload_all'])"
                v-on:found="on_scan"
                :input_placeholder="search_input_placeholder"
                />
            <batch-picking-line-actions
                v-if="state_is('start_line')"
                v-on:action="state.on_action"
                />
            <div v-if="state_is('scan_destination')">
                <div class="qty">
                    <input-number-spinner :init_value="scan_destination_qty" class="mb-2"/>
                </div>
                <searchbar
                    v-on:found="on_scan"
                    :input_placeholder="search_input_placeholder"
                    />
                <div class="full-bin text-center">
                    <v-btn depressed color="warning" @click="state.on_action_full_bin">
                        Full bin
                    </v-btn>
                </div>
            </div>
            <stock-zero-check
                v-if="state_is('zero_check')"
                v-on:action="state.on_action"
                />
        </Screen>
    `,
    computed: {
        batch_id: function () {
            return this.erp_data.data.confirm_start.id
        },
    },
    methods: {
        action_full_bin: function () {
            this.go_state(
                'wait_call',
                this.odoo.prepare_unload(this.batch_id)
            )
        },
    },
    data: function () {
        return {
            'usage': 'cluster_picking',
            'initial_state_key': 'start',
            'current_state_key': 'start',
            'scan_destination_qty': 1,
            'states': {
                'start': {
                    enter: () => {
                        this.reset_erp_data('data')
                    },
                    on_get_work: (evt) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.find_batch()
                        )
                    },
                    on_manual_selection: (evt) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.picking_batch()
                        )
                    },
                },
                'start_manual_selection': {
                    on_submit_back: () => {
                        this.go_state('start')
                    },
                    on_select: (selected) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.select(selected)
                        )
                    },
                },
                'confirm_start': {
                    on_confirm: () => {
                        this.go_state(
                            'wait_call',
                            this.odoo.confirm_start(this.state.data)
                        )
                    },
                    on_cancel: () => {
                        this.go_state(
                            'wait_call',
                            this.odoo.unassign(this.state.data)
                        )
                    } 
                },
                'start_line': {
                    // here we have to use some info sent back from `select`
                    // or from `find_batch` that we pass to scan line
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.scan_line(this.state.data, scanned.text)
                        )
                    },
                    scan_placeholder: 'Scan location / pack / product / lot',
                    // additional actions
                    on_action: (action) => {
                        this.state['on_' + action].call(this)
                    },
                    on_action_full_bin: () => {
                        this.action_full_bin()
                    },
                    on_action_skip_line: () => {
                        console.log('skip line TODO')
                    },
                    on_action_stock_out: () => {
                        console.log('stock out TODO')
                    },
                    on_action_change_pack_or_lot: () => {
                        console.log('change pack or lot TODO')
                    },
                },
                'scan_destination': {
                    enter: () => {
                        // TODO: shalle we hook v-model for qty input straight to the state data?
                        this.scan_destination_qty = this.erp_data.data.start_line.pack.qty
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.scan_destination_pack(
                                this.state.data, scanned.text, this.scan_destination_qty)
                        )
                    },
                    on_action_full_bin: () => {
                        this.action_full_bin()
                    },
                    on_button_action: () => {
                        this.go_state(
                            'wait_call',
                            this.odoo.prepare_unload(scanned.text)
                        )
                    },
                    scan_placeholder: 'Scan destination bin',
                },
                'zero_check': {
                    on_action: (action) => {
                        this.state['on_' + action].call(this)
                    },
                    on_action_confirm_zero: () => {
                        this.go_state(
                            'wait_call',
                            this.odoo.stock_is_zero(true)
                        )
                    },
                    on_action_confirm_not_zero: () => {
                        this.go_state(
                            'wait_call',
                            this.odoo.stock_is_zero(false)
                        )
                    },
                },
                'unload_all': {
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.set_destination_all(
                                this.state.data, scanned.text)
                        )
                    },
                    scan_placeholder: 'Scan location',
                },
                'show_completion_info': {
                    on_confirm: () => {
                        // TODO: turn the cone?
                        this.go_state('start')
                    },
                },
            }
        }
    },
})
