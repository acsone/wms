import {ScenarioBaseMixin} from "./mixins.js";

Vue.component('scan-anything', {
    mixins: [ScenarioBaseMixin],
    template: `
        <Screen title="Scan Anything">
            <searchbar v-on:found="on_scan" :input_placeholder="search_input_placeholder"></searchbar>
            <user-information v-if="!need_confirmation && user_notification.message" v-bind:info="user_notification"></user-information>
            <detail-pack :packDetail="erp_data.data" v-if="erp_data.data.type=='pack'"></detail-pack>
            <detail-product :productDetail="erp_data.data.detail_info" v-if="erp_data.data.type=='product'"></detail-product>
            <detail-location :locationDetail="erp_data.data.detail_info" v-if="erp_data.data.type=='location'"></detail-location>
            <detail-operation :operationDetail="erp_data.data.detail_info" v-if="erp_data.data.type=='operation'"></detail-operation>
            <reset-screen-button v-on:reset="on_reset" :show_reset_button="show_reset_button"></reset-screen-button>
        </Screen>
    `,
    data: function () {
        return {
            'usage': 'scan_anything',
            'show_reset_button': true,
            'initial_state': 'scan_something',
            'current_state': 'scan_something',
            'state': {
                'scan_something': {
                    enter: () => {
                        this.reset_erp_data('data')
                    },
                    on_scan: (scanned) => {
                        this.go_state(
                            'wait_call',
                            this.odoo.scan_anything(scanned.text)
                        )
                    },
                    scan_placeholder: 'Scan anything...',
                },
                'wait_call': {
                    success: (result) => {
                        if (result.data != undefined)
                            this.set_erp_data('data', result.data)
                        this.go_state('show_detail_info')
                    },
                    error: (result) => {
                        this.go_state('scan_something')
                    },
                },
                'show_detail_info': {
                    enter: () => {
                        this.erp_data.data.location_barcode = false
                    },
                    on_scan: (scanned) => {
                        this.erp_data.data.location_barcode = scanned.text
                        this.go_state('wait_call',
                            this.odoo.scan_anything(scanned.text))
                    },
                },
            }
        }
    },
})
