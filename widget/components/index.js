import Widget from "./Widget.vue";
import { createApp } from "vue";
import {_createI18n, _createPinia} from "../plugins";

function _buildApp(props) {
    return createApp(Widget, { ...props }).use(_createPinia()).use(_createI18n())
}

class ChatfaqWidget {
    constructor({ element, chatfaqApi, chatfaqWs, fsmDef, manageUserId, userId, title, subtitle, maximized, fullScreen, historyOpened, widgetConfigId, displayGeneration, displaySources, sourcesFirst, lang }) {
        if (typeof element == "string")
            element = document.querySelector(element)
        this.element = element;

        const props = { ...element.dataset }
        props['chatfaqApi'] = chatfaqApi;
        props['chatfaqWs'] = chatfaqWs
        props['fsmDef'] = fsmDef
        props['maximized'] = maximized
        props['fullScreen'] = fullScreen
        props['historyOpened'] = historyOpened
        props['widgetConfigId'] = widgetConfigId
        props['manageUserId'] = manageUserId
        props['displayGeneration'] = displayGeneration
        props['displaySources'] = displaySources
        props['sourcesFirst'] = sourcesFirst
        props['lang'] = lang

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
        if(this.dataset.maximized === "false")
            delete this.dataset.maximized
        if(this.dataset.fullScreen === "false")
            delete this.dataset.fullScreen
        if(this.dataset.historyOpened === "false")
            delete this.dataset.historyOpened
        if(this.dataset.manageUserId === "false")
            delete this.dataset.manageUserId
        if(this.dataset.displayGeneration === "false")
            delete this.dataset.displayGeneration
        if(this.dataset.displaySources === "false")
            delete this.dataset.displaySources
        if(this.dataset.sourcesFirst === "false")
            delete this.dataset.sourcesFirst

        const app = _buildApp(this.dataset);
        app.mount(this)
    }
}

export { ChatfaqWidgetCustomElement, ChatfaqWidget };
