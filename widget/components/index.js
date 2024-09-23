import Widget from "./Widget.vue";
import { createApp } from "vue";
import {_createI18n, _createPinia} from "../plugins";

function _buildApp(props) {
    return createApp(Widget, { ...props }).use(_createPinia()).use(_createI18n())
}

class ChatfaqWidget {
    constructor({ element, chatfaqApi, chatfaqWs, fsmDef, manageUserId, userId, title, subtitle, startSmallMode, fullScreen, startWithHistoryClosed, widgetConfigId, hideSources, sourcesFirst, lang, previewMode, customCss, initialConversationMetadata }) {
        if (typeof element == "string")
            element = document.querySelector(element)
        this.element = element;

        const props = { ...element.dataset }
        props['chatfaqApi'] = chatfaqApi;
        props['chatfaqWs'] = chatfaqWs
        props['fsmDef'] = fsmDef
        props['fullScreen'] = fullScreen
        props['widgetConfigId'] = widgetConfigId
        props['manageUserId'] = manageUserId
        props['sourcesFirst'] = sourcesFirst
        props['lang'] = lang
        props['previewMode'] = previewMode
        props['customCss'] = customCss
        props['initialConversationMetadata'] = initialConversationMetadata

        props['startWithHistoryClosed'] = startWithHistoryClosed
        props['startSmallMode'] = startSmallMode
        props['hideSources'] = hideSources

        if (userId)
            props['userId'] = userId;
        if (title)
            props['title'] = title;
        if (subtitle)
            props['subtitle'] = subtitle

        this.app = _buildApp(props);
    }

    mount() {
        this.app.mount(this.element)
    }
}

// couldn't implement this: https://rimdev.io/vue-3-custom-elements cause shadow dom problems (Rollup does not include 'styles' inside the .ce.vue element)
// a possible solution is to use Vite istead of Rollup as such: https://maximomussini.com/posts/vue-custom-elements
// for the moment we just implemented: https://github.com/vuejs/vue-web-component-wrapper/issues/93#issuecomment-909136116
class ChatfaqWidgetCustomElement extends HTMLElement {
    connectedCallback() {
        const app = _buildApp(this.dataset);
        app.mount(this)
    }
}

export { ChatfaqWidgetCustomElement, ChatfaqWidget };
