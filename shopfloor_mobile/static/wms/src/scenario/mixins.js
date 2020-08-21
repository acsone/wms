export var ScenarioBaseMixin = {
    data: function() {
        return {
            messages: {
                message: {
                    body: "",
                    message_type: "",
                },
                popup: {
                    body: "",
                },
            },
            need_confirmation: false,
            show_reset_button: false,
            initial_state_key: "start",
            current_state_key: "",
            states: {},
            usage: "", // Match component usage on odoo,
            menu_item_id: false,
        };
    },
    watch: {
        "$route.params.menu_id": function() {
            this.menu_item_id = this._get_menu_item_id();
        },
    },
    created: function() {
        this.menu_item_id = this._get_menu_item_id();
    },
    beforeRouteUpdate(to, from, next) {
        // Load initial state
        this._state_load(to.params.state);
        next();
    },
    beforeMount: function() {
        /*
        Ensure initial state is set.
        beforeRouteUpdate` runs only if the route has changed,
        which means that if your reload the page it won't get called :(
        We could use `beforeRouteEnter` but that's not tied to the current instance
        and we won't be able to call `_state_load`.
        */
        this._state_load(this.$route.params.state);
    },
    computed: {
        odoo: function() {
            const odoo_params = {
                process_menu_id: this.menu_item_id,
                profile_id: this.$root.profile.id,
                usage: this.usage,
            };
            return this.$root.getOdoo(odoo_params);
        },
        /*
        Full object of current state.
        TODO: for a future refactoring consider moving out of data `states`
        they are not really data that changes and then we can make them
        standalone object w/ their own class.
        */
        state: function() {
            const state = {
                key: this.current_state_key,
                data: this.state_get_data(),
            };
            _.extend(state, this.states[this.current_state_key]);
            _.defaults(state, {display_info: {}});
            return state;
        },
        search_input_placeholder: function() {
            const placeholder = this.state.display_info.scan_placeholder;
            return _.isFunction(placeholder) ? placeholder.call(this) : placeholder;
        },
        show_cancel_button: function() {
            return this.state.display_info.show_cancel_button;
        },
        screen_info: function() {
            return {
                // you can provide a different screen title
                title: this.screen_title ? this.screen_title() : this.menu_item().name,
                current_doc: this.current_doc ? this.current_doc() : null,
                klass: this.screen_klass(),
                user_message: this.user_message,
                user_popup: this.user_popup,
                noUserMessage: this.need_confirmation,
            };
        },
        user_message: function() {
            if (_.result(this.messages, "message.body")) {
                return this.messages.message;
            }
            return null;
        },
        user_popup: function() {
            if (_.result(this.messages, "popup.body")) {
                return this.messages.popup;
            }
            return null;
        },
    },
    methods: {
        _get_menu_item_id: function() {
            const menu_id = Number.parseInt(this.$route.params.menu_id, 10);
            if (Number.isNaN(menu_id)) {
                /*
                It's very handy for demo data to reference always the same menu id.
                Since the menu id is included in the URL
                it allows to reload the page w/out having to refresh menu items.
                This way you can define multiple scenario w/ different menu items
                and you can tag them with the same reusable label (eg: case_1).
                */
                return this.$route.params.menu_id;
            }
            return menu_id;
        },
        screen_klass: function() {
            return this.usage + " " + "state-" + this.state.key;
        },
        menu_item: function() {
            const self = this;
            return _.head(
                _.filter(this.$root.appmenu.menus, function(m) {
                    return m.id === self.menu_item_id;
                })
            );
        },
        make_state_component_key: function(bits) {
            bits.unshift(this.current_state_key);
            bits.unshift(this.usage);
            return this.make_component_key(bits);
        },
        storage_key: function(state_key) {
            state_key = _.isUndefined(state_key) ? this.current_state_key : state_key;
            return this.usage + "." + state_key;
        },
        /*
        Switch state to given one.
        */
        state_to: function(state_key) {
            const self = this;
            return this.$router
                .push({
                    name: this.usage,
                    params: {
                        menu_id: this.menu_item_id,
                        state: state_key,
                    },
                })
                .catch(() => {
                    // see https://github.com/quasarframework/quasar/issues/5672
                    console.error("No new route found");
                });
        },
        // Generic states methods
        state_is: function(state_key) {
            return state_key == this.current_state_key;
        },
        state_in: function(state_keys) {
            return _.filter(state_keys, this.state_is).length > 0;
        },
        state_reset_data: function(state_key) {
            state_key = state_key || this.current_state_key;
            this.$root.$storage.remove(this.storage_key(state_key));
            this.$set(this.states[state_key], "data", {});
        },
        _state_get_data: function(state_key) {
            return this.$root.$storage.get(this.storage_key(state_key), {});
        },
        _state_set_data: function(state_key, v) {
            this.$root.$storage.set(this.storage_key(state_key), v);
            this.$set(this.states[state_key], "data", v);
        },
        state_get_data: function(state_key) {
            state_key = state_key || this.current_state_key;
            return this._state_get_data(state_key);
        },
        state_set_data: function(data, state_key) {
            state_key = state_key || this.current_state_key;
            const new_data = _.merge({}, this.state_get_data(state_key), data);
            // Trigger update of computed `state.data` and refreshes the UI.
            this._state_set_data(state_key, new_data);
        },
        state_reset_data_all() {
            const self = this;
            const keys_to_clear = _.filter(this.$storage.keys(), x => {
                return x.includes(self.usage);
            });
            keys_to_clear.forEach(key => {
                // Key includes the whole string w/ prefix, need the state key only
                self.state_reset_data(_.last(key.split(".")));
            });
        },
        /*
            Load given state, handle transition, setup event handlers.
        */
        _state_load: function(state_key, promise) {
            if (state_key == "init") {
                /*
                Alias "init" to the initial state
                and erase all existing data if any.
                Used when we enter from a menu or to enforce data cleanup
                or any other case where you want to erase all data on demand.
                */
                this.state_reset_data_all();
                /**
                 * Special case: if `init` is defined as state
                 * you can use it do particular initialization.
                 * Eg: call the server to preload some data.
                 * In this case the state is responsible
                 * for handline the transition to another state
                 * or delegate it to server result via `next_state` key.
                 */
                if (!("init" in this.states)) {
                    state_key = this.initial_state_key;
                }
            }
            state_key = state_key || "start";
            if (state_key == "start") {
                // Alias "start" to the initial state
                state_key = this.initial_state_key;
            }
            if (!_.has(this.states, state_key)) {
                alert("State `" + state_key + "` does not exists!");
            }
            this.on_state_exit();
            this.current_state_key = state_key;
            if (promise) {
                promise.then();
            } else {
                this.on_state_enter();
            }
            this._state_bind_events();
            // notify root
            // TODO: maybe not needed after introducing routing
            this.$root.$emit("state:change", this._global_state_key(state_key));
        },
        _global_state_key: function(state_key) {
            return this.usage + "/" + state_key;
        },
        // TODO: refactor all transitions to state `wait_call` with this call
        wait_call: function(promise, callback) {
            return promise.then(this.on_call_success, this.on_call_error);
        },
        on_state_enter: function() {
            if (this.state.enter) {
                this.state.enter();
            }
        },
        on_state_exit: function() {
            if (this.state.exit) {
                this.state.exit();
            }
        },
        on_call_success: function(result) {
            if (_.isUndefined(result)) {
                console.error(result);
                alert("Something went wrong. Check log.");
            }
            if (result.error) {
                this.display_app_error(result.error);
                return;
            }
            const state_key =
                result.next_state == "start"
                    ? this.initial_state_key
                    : result.next_state;
            if (!_.isUndefined(result.data)) {
                this.state_reset_data(state_key);
                this.state_set_data(result.data[state_key], state_key);
            }
            this.reset_notification();
            if (result.message) {
                this.set_message(result.message);
            }
            if (result.popup) {
                this.set_popup(result.popup);
            }
            if (this.current_state_key != state_key) {
                this.state_to(state_key);
            }
        },
        on_call_error: function(result) {
            alert(result.status + " " + result.error);
        },
        on_reset: function(e) {
            this.state_reset_data_all();
            this.reset_notification();
            this.state_to("start");
        },
        // Specific states methods
        on_scan: function(scanned) {
            if (this.state.on_scan) {
                this.state.on_scan(scanned);
            }
        },
        // TODO: check if we really need these
        // as we have state event handlers auto binding.
        // on_select: function(selected) {
        //     if (this.state.on_select) {
        //         this.state.on_select(selected);
        //     }
        // },
        // on_back: function() {
        //     if (this.state.on_back) {
        //         this.state.on_back();
        //     }
        // },
        // TODO: get rid of this as it's used on cluster_picking only and
        // we can use state events binding.
        on_cancel: function() {
            if (this.state.on_cancel) {
                this.state.on_cancel();
            }
        },
        on_user_confirm: function(answer) {
            this.state.on_user_confirm(answer);
            this.need_confirmation = false;
            this.reset_notification();
        },
        set_message: function(message) {
            this.$set(this.messages, "message", message);
        },
        set_popup: function(popup) {
            this.$set(this.messages, "popup", popup);
        },
        reset_notification: function() {
            this.$set(this.messages, "message", {body: null, message_type: null});
            this.$set(this.messages, "popup", {body: null});
        },
        display_app_error: function(error) {
            this.set_message({
                body: error.description,
                message_type: "error",
            });
        },
        _state_bind_events: function() {
            if (this.state.events) {
                /*
                Automatically bind events defined by states.
                A state can define `events` w/ this structure:

                    events: {
                        '$event_name': '$handler',
                    },

                `$handler_name` must match a function or the name of a function
                available in the state.

                The event name is prefixed w/ the state key so that
                any component can subscribe globally,
                via the event hub at root level,
                to a particular event fired on a specific state
                */
                const self = this;
                _.each(self.state.events, function(handler, name) {
                    if (typeof handler == "string") handler = self.state[handler];
                    const event_name =
                        self._global_state_key(self.state.key) + ":" + name;
                    const existing = self.$root.event_hub._events[event_name];
                    if (handler && _.isEmpty(existing)) {
                        self.$root.event_hub.$on(event_name, handler);
                    }
                });
            }
        },
    },
};
