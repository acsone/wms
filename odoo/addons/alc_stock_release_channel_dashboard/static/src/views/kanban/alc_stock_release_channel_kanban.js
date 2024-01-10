/** @odoo-module **/
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {memoize} from "@web/core/utils/functions";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const get_pricking_todo_view = memoize(async function (orm) {
  const views = await orm.searchRead(
    "ir.ui.view",
    [["name", "=", "stock.picking.batch.candidate.tree"]],
    ["id", "name", "model", "type"],
    {limit: 1}
  );
  return views[0];
});

export class AlcStockReleaseChannelKanbanController extends KanbanController {
  setup() {
    super.setup();
    this.orm = useService("orm");
    this.actionService = useService("action");
  }

  async onClickOpenPickingsToDo() {
    const view = await get_pricking_todo_view(this.orm);
    const domain = await this.orm.call(
      "stock.picking",
      "get_released_batch_candidates_domain",
      [],
      {}
    );
    this.actionService.doAction({
      type: "ir.actions.act_window",
      name: this.env._t("Pickings to do"),
      res_model: view.model,
      views: [
        [view.id, view.type],
        [false, "form"],
      ],
      view_mode: "list",
      target: "current",
      domain,
    });
  }
}

registry.category("views").add("alc_stock_release_channel_kanban", {
  ...kanbanView,
  Controller: AlcStockReleaseChannelKanbanController,
  buttonTemplate: "alc_stock_release_channel_kanban.Buttons",
});
