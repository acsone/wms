/**
 * Copyright 2021 ACSONE SA/NV (http://www.acsone.eu)
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

//  Override main menu template
let methods = Vue.component("detail-location").extendOptions.methods;
Vue.component("detail-location").extendOptions.methods = {
  ...methods,
  ...{
    available_product_list_options() {
      return {
        main: true,
        key_title: "display_name",
        klass: "loud-labels",
        title_action_field: {
          action_val_path: "default_code",
        },
        fields: this.available_product_list_fields(),
      };
    },
    available_product_list_fields() {
      return [
        {path: "supplier_code", label: "Vendor code", klass: "loud"},
        {path: "quantity", label: "Qty in stock"},
      ];
    },
    lot_detail_options() {
      return {
        main: false,
        key_title: "name",
        fields: this.lot_detail_fields(),
        klass: "loud-labels",
      };
    },
    lot_detail_fields() {
      const self = this;
      return [
        {path: "quantity", label: "Qty in stock"},
        {
          path: "expire_date",
          label: "Expiry date",
          renderer: function(rec, field) {
            return self.utils.display.render_field_date(rec, field);
          },
        },
        {
          path: "removal_date",
          label: "Removal date",
          renderer: function(rec, field) {
            return self.utils.display.render_field_date(rec, field);
          },
        },
      ];
    },
  },
};

Vue.component("detail-location").extendOptions.template = `
 <div :class="$options._componentTag">
    <item-detail-card
      v-bind="$props"
      :options="{main: true}"
      :card_color="utils.colors.color_for('detail_main_card')">

      <template v-slot:subtitle>
        {{ record.complete_name }}
      </template>

    </item-detail-card>
    <div class="reserved_products" v-if="record.reserved_operations.length">
        <separator-title>Reserved products</separator-title>

        <list
            :records="record.reserved_operations"
            :options="product_list_options()"
            />

    </div>

    <div class="available_products" v-if="record.products.length">
        <separator-title>Available products</separator-title>

        <v-expansion-panels v-if="record.products.length > 0" flat :color="utils.colors.color_for('detail_main_card')">
            <v-expansion-panel v-for="(product, index) in record.products" :key="make_component_key(['product', index])">
                <v-expansion-panel-header>
                    <item-detail-card
                        v-bind="$props"
                        :record="product"
                        :key="make_component_key(['product', product.id])"
                        :options="available_product_list_options()"
                        :card_color="utils.colors.color_for('detail_main_card')"
                        />
                </v-expansion-panel-header>
                <v-expansion-panel-content>
                <item-detail-card
                    v-for="(lot, i) in product.lots"
                    :record="lot"
                    v-bind="$props"
                    :key="make_component_key(['lot', lot.id])"
                    :options="lot_detail_options()"
                    :card_color="utils.colors.color_for('screen_step_todo')"
                    />
                </v-expansion-panel-content>
            </v-expansion-panel>
        </v-expansion-panels>
        <!-- list
            :records="record.products"
            :options="available_product_list_options()"
            /-->

    </div>

  </div>
`;
