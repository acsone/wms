import {translation_registry} from "/shopfloor_mobile_base/static/wms/src/services/translation_registry.js";

function loadJSON(callback, url) {
  const xobj = new XMLHttpRequest();
  xobj.overrideMimeType("application/json");
  xobj.open("GET", url, false); // False -> synchronous call to be sure to  have the result before the registery is used by others JS
  xobj.onreadystatechange = function () {
    if (xobj.readyState == 4 && xobj.status == "200") {
      callback(xobj.responseText);
    }
  };
  xobj.send(null);
}

loadJSON((json) => {
  const messages = JSON.parse(json);
  const original_messages = translation_registry.get("en-US");
  const merged_messages = {...messages, ...original_messages};
  translation_registry.add("en-US", merged_messages);
}, "/alc_shopfloor_mobile_cluster_picking/static/src/js/i18n/en.json");

loadJSON((json) => {
  const messages = JSON.parse(json);
  const original_messages = translation_registry.get("fr-FR");
  const merged_messages = {...messages, ...original_messages};
  translation_registry.add("fr-FR", merged_messages);
}, "/alc_shopfloor_mobile_cluster_picking/static/src/js/i18n/fr.json");
