/**
 * Copyright 2022 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */

Vue.component("picking-detail", {
  props: ["record"],
  methods: {
    detail_fields() {
      return [{path: "name", renderer: this.render_infos}];
    },
    render_infos(record, field) {
      return [
        record.name + " -",
        " Op: " + record.move_line_count + ", ",
        "Weight: " + Math.round(record.weight * 100) / 100 + " kg",
      ].join(" ");
    },
  },
  template: `
    <div class="detail with-bottom-actions" v-if="!_.isEmpty(record)">
      <div class="review">
      <item-detail-card :card_color="utils.colors.color_for('screen_step_todo')"
      :record="record" :options="{no_title:true, fields: detail_fields()}" />
      </div>
    </div>
  `,
});
