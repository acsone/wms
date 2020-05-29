export var batch_picking_line = Vue.component("batch-picking-line-detail", {
    props: {
        line: Object,
        // TODO: not sure this is still needed
        showFullInfo: {
            type: Boolean,
            default: true,
        },
        articleScanned: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        return {
            dialog: false,
        };
    },
    computed: {
        has_destination_pack() {
            return _.result(this.line, "package_dest.id");
        },
    },
    methods: {
        detail_fields(key) {
            const mapping = {
                location_src: [],
                product: [
                    {path: "package_src.name", label: "Pack"},
                    {path: "quantity", label: "Qty"},
                    {path: "product.qty_available", label: "Qty on hand"},
                    {path: "lot.name", label: "Lot"},
                ],
                location_dest: [],
            };
            return mapping[key];
        },
        full_detail_fields() {
            return [
                {path: "batch.name", label: "Batch"},
                {path: "picking.name", label: "Picking"},
                {path: "picking.origin", label: "Origin"},
                {path: "picking.partner.name", label: "Customer"},
                {path: "location_dest.name", label: "Destination"},
            ];
        },
    },
    template: `
<div v-if="!_.isEmpty(line)" :class="'detail batch-picking-line-detail ' + (line.postponed ? 'line-postponed' : '')">

  <item-detail-card
    :key="'batch-picking-line-detail-1'"
    :record="line"
    :options="{main: true, key_title: 'location_src.name', fields: detail_fields('location_src'), title_action_field: {action_val_path: 'location_src.barcode'}}"
    :card_color="utils.colors.color_for('screen_step_done')"
    />
  <item-detail-card
    :key="'batch-picking-line-detail-2'"
    :record="line"
    :options="{main: true, key_title: 'product.display_name', fields: detail_fields('product'), title_action_field:  {action_val_path: 'product.barcode'}}"
    :card_color="utils.colors.color_for(articleScanned ? 'screen_step_done': 'screen_step_todo')"
    />

  <item-detail-card
    v-if="articleScanned && has_destination_pack"
    :key="'batch-picking-line-detail-3'"
    :record="line"
    :options="{main: true, key_title: 'package_dest.name', title_action_field:  {action_val_path: 'package_dest.name'}}"
    :card_color="utils.colors.color_for(has_destination_pack ? 'screen_step_done': 'screen_step_todo')"
    />

  <item-detail-card
    v-if="articleScanned && !has_destination_pack"
    :key="'batch-picking-line-detail-4'"
    :record="line"
    :options="{main: true, title_action_field:  {action_val_path: 'name'}}"
    :card_color="utils.colors.color_for(has_destination_pack ? 'screen_step_done': 'screen_step_todo')"
    >
    <template v-slot:title>
      Destination pack not selected.
    </template>
  </item-detail-card>

  <!--
  <v-expansion-panels>
    <v-expansion-panel class="with-card">
      <v-expansion-panel-header>Full details</v-expansion-panel-header>
      <v-expansion-panel-content>
        <item-detail-card
          :key="'batch-picking-line-detail-4'"
          :record="line"
          :options="{no_title: true, loud_labels: true, no_outline: true, fields: full_detail_fields()}"
          />
      </v-expansion-panel-content>
    </v-expansion-panel>
  </v-expansion-panels>
  -->

  <todo>Missing package qty widget</todo>

</div>
`,
});

export var batch_picking_line_actions = Vue.component("batch-picking-line-actions", {
    props: ["line"],
    data() {
        return {
            dialog: false,
        };
    },
    methods: {
        handle_action(action) {
            this.$emit("action", action);
            this.dialog = false;
        },
    },
    template: `
  <div class="batch-picking-line-actions">
    <v-dialog v-model="dialog" fullscreen tile class="actions fullscreen text-center">
      <template v-slot:activator="{ on }">
        <div class="button-list button-vertical-list full">
          <v-row class="actions bottom-actions">
            <v-col class="text-center" cols="12">
              <btn-action v-on="on">Action</btn-action>
            </v-col>
          </v-row>
        </div>
      </template>
      <v-card>
        <div class="button-list button-vertical-list full">
          <v-row align="center">
            <v-col class="text-center" cols="12">
              <btn-action @click="handle_action('action_full_bin')">Go to destination - full bin(s)</btn-action>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col class="text-center" cols="12">
              <btn-action @click="handle_action('action_skip_line')">Skip line</btn-action>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col class="text-center" cols="12">
              <btn-action
                  @click="handle_action('action_stock_out')">Declare stock out</btn-action>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col class="text-center" cols="12">
              <btn-action @click="handle_action('action_change_pack_or_lot')">Change lot or pack</btn-action>
            </v-col>
          </v-row>
          <v-row align="center">
            <v-col class="text-center" cols="12">
              <v-btn x-large @click="dialog = false">Back</v-btn>
            </v-col>
          </v-row>
        </div>
      </v-card>
    </v-dialog>
  </div>
`,
});

export var batch_picking_line_stock_out = Vue.component(
    "batch-picking-line-stock-out",
    {
        props: ["line"],
        methods: {
            handle_action(action) {
                this.$emit("action", action);
            },
        },
        template: `
    <div class="batch-picking-line-stock-out">
      <batch-picking-line-detail :line="line" />
      <div class="button-list button-vertical-list full">
        <v-row align="center">
          <v-col class="text-center" cols="12">
            <btn-action @click="handle_action('confirm_stock_issue')">Confirm stock = 0</btn-action>
          </v-col>
        </v-row>
        <v-row align="center">
          <v-col class="text-center" cols="12">
            <v-btn x-large color="default" @click="handle_action('back')">back</v-btn>
          </v-col>
        </v-row>
      </div>
    </div>
`,
    }
);
