import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";
import {loadTranslation} from "/shopfloor_mobile_base/static/wms/src/i18n/load_translation.js";

loadTranslation(json => {
    const messages = JSON.parse(json);
    const original_messages = translation_registry.get("fr-FR");
    const merged_messages = {...messages, ...original_messages};
    translation_registry.add("fr-FR", merged_messages);
}, "/shopfloor_mobile_base/static/wms/src/i18n/fr.json");

loadTranslation(json => {
    const messages = JSON.parse(json);
    const original_messages = translation_registry.get("en-US");
    const merged_messages = {...messages, ...original_messages};
    translation_registry.add("en-US", merged_messages);
}, "/shopfloor_mobile_base/static/wms/src/i18n/en.json");
