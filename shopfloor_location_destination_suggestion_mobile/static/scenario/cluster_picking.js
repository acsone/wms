/**
 * Copyright 2025 ACSONE SA/NV (https://acsone.eu)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
 */

const location_operation_detail_component = Vue.component(
    "detail-location-destination-operation"
);
const methods = location_operation_detail_component.extendOptions.methods;
const location_operation_detail_fields_method =
    methods.location_operation_detail_fields;

// Adds the destination locations suggestions to the destination location component
methods.location_operation_detail_fields = function () {
    const result = location_operation_detail_fields_method.bind(this)();
    const new_result = [
        ...result,
        {path: "location_destination_suggestions", label: "Destination Suggestions"},
    ];
    return new_result;
};

const created_original =
    location_operation_detail_component.extendOptions.created || function () {};

const created_method = function () {
    created_original.bind(this)();
    // Manipulate the 'record' object before the component is rendered
    if (this.record) {
        const location_dest_name = this.record.location_dest?.name || "";
        if (this.record.location_destination_suggestions) {
            this.record.title =
                location_dest_name +
                " => " +
                this.record.location_destination_suggestions;
        } else {
            this.record.title = this.record.location_dest?.name || "";
        }
    }
};
location_operation_detail_component.extendOptions.created = created_method;

// override the title to display the destination location name and suggestion
const location_operation_detail_options_method =
    methods.location_operation_detail_options;
methods.location_operation_detail_options = function () {
    const result = location_operation_detail_options_method.bind(this)();
    result.key_title = "title";
    return result;
};
