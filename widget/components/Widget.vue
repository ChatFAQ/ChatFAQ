<template>
    <Suspense v-if="initialized">
        <div class="chatfaq-widget" :class="{
            'fit-to-parent': store.fitToParent
        }">
            <div v-if="isPhoneLandscape" class="not-supported">
                <div class="not-supported-text">
                    <div class="not-supported-text-title">Sorry, we don't support mobile landscape mode yet.</div>
                    <div class="not-supported-text-subtitle">Please, turn your phone to portrait mode.</div>
                </div>
            </div>
            <div v-if="store.opened && !isPhoneLandscape" class="widget-wrapper"
                 :class="{'history': store.historyOpened, 'full-screen': store.fullScreen, 'fit-to-parent': store.fitToParent}">
                <div class="dark-filter" v-if="store.historyOpened"></div>
                <LeftMenu v-if="store.historyOpened" class="widget-history"
                          :class="{'maximized': store.maximized, 'full-screen': store.fullScreen}"/>
                <div class="widget-body"
                     :class="{'maximized': store.maximized, 'full-screen': store.fullScreen, 'history-closed': !store.historyOpened, 'fit-to-parent': store.fitToParent}">
                    <Header v-if="!store.noHeader" class="header" :class="{'history': store.historyOpened, 'full-screen': store.fullScreen}"/>
                    <Chat class="chat" :class="{'history': store.historyOpened, 'full-screen': store.fullScreen, 'no-header': store.noHeader}"/>
                </div>
            </div>
            <div v-if="!isPhoneLandscape && !store.fullScreen && !store.fitToParent" class="widget-open-button" :class="{'opened': store.opened}"
                 @click="store.opened = !store.opened">
                <BubbleButtonClose v-if="store.opened" class="bubble-icon close" color="white" icon="'~/assets/icons/bubble-button-open.svg'" />
                <BubbleButtonOpen v-else class="bubble-icon open" color="white" icon="'~/assets/icons/bubble-button-open.svg'" />
            </div>
        </div>
    </Suspense>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import { useHead } from "@unhead/vue";
import {ref, defineProps, onMounted, watch} from "vue";
import LeftMenu from "~/components/left-menu/LeftMenu.vue";
import Header from "~/components/chat/Header.vue";
import Chat from "~/components/chat/Chat.vue";
import BubbleButtonOpen from "~/components/icons/BubbleButtonOpen.vue";
import BubbleButtonClose from "~/components/icons/BubbleButtonClose.vue";
import {getUserId} from "~/utils";
import { useI18n } from "vue-i18n";
const i18n = useI18n();

const store = useGlobalStore();
const isPhoneLandscape = ref(false);
const initialized = ref(false);

useHead({
    meta: [
        {name: 'maximum-scale', content: 1}
    ],
})

const props = defineProps({
    chatfaqWs: String,
    chatfaqApi: String,
    fsmDef: String,
    userId: String,
    title: String,
    subtitle: String,
    startSmallMode: Boolean,
    fullScreen: Boolean,
    startWithHistoryClosed: Boolean,
    conversationId: String,
    widgetConfigId: String,
    hideSources: Boolean,
    hideToolMessages: Boolean,
    sourcesFirst: Boolean,
    onlyChat: Boolean,
    fitToParent: Boolean,
    lang: String,
    previewMode: Boolean,
    customCss: String,
    initialConversationMetadata: String,
    stateOverride: String,
    customIFramedMsgs: String,
    stickInputPrompt: Boolean,
    speechRecognition: Boolean,
    speechRecognitionLang: String,
    speechRecognitionAutoSend: Boolean,
    speechRecognitionAlwaysOn: Boolean,
    speechRecognitionBeep: Boolean,
    speechRecognitionPhraseActivation: String,
    allowAttachments: Boolean,
    authToken: String,
    disableDayNightMode: Boolean,
    enableLogout: Boolean,
    enableResend: Boolean,
    speechSynthesis: Boolean,
    speechSynthesisPitch: Number,
    speechSynthesisRate: Number,
    speechSynthesisVoices: String,
    speechSynthesisEnabledByDefault: Boolean,
});

const jsonProps = [
    "initialConversationMetadata",
    "stateOverride",
    "customIFramedMsgs"
]

let data = props

const _customCss = ref(props.customCss)
watch( () => props.customCss, async (newVal, _)=> {
    _customCss.value = newVal
    await init()
}, {immediate: true, deep: true})
async function init() {
    if(_customCss.value) {
        const customCss = document.getElementById("custom-css");
        if (customCss)
            customCss.remove();
        const style = document.createElement('style');
        style.id = "custom-css";
        style.innerHTML = _customCss.value;
        document.head.appendChild(style);
    }

    if (props.widgetConfigId !== undefined) {
        const headers = {
            'widget-id': props.widgetConfigId,
        }
        if (props.authToken)
            headers.Authorization = `Token ${props.authToken}`;

        const response = await chatfaqFetch(props.chatfaqApi + `/back/api/widget/widgets/${props.widgetConfigId}/`, { headers });
        let server_data = await response.json();
        // sneak case data keys to lowerCamelCase:
        server_data = Object.keys(server_data).reduce((acc, key) => {
            acc[key.replace(/_([a-z])/g, (g) => g[1].toUpperCase())] = server_data[key];
            return acc;
        }, {});

        const merged_data = {}
        for (const key in data) {
            if (jsonProps.indexOf(key) > -1) {
                if (typeof data[key] == "string" && data[key].length > 0)
                    data[key] = JSON.parse(data[key] || "{}")
                merged_data[key] = {...data[key], ...server_data[key]}
            }
            else
                merged_data[key] = data[key] || server_data[key]
        }
        for (const key in server_data) {
            if (data[key] === undefined)
                merged_data[key] = server_data[key]
        }
        data = merged_data

        const style = document.createElement('style');
        style.innerHTML = data.css;
        document.head.appendChild(style);
    }
    initStore()
}

function initStore() {
    if (data.previewMode) {
        store.setPreviewMode()
    }
    store.chatfaqWS = data.chatfaqWs;
    store.chatfaqAPI = data.chatfaqApi;
    store.userId = data.userId;
    store.initialSelectedPlConversationId = data.conversationId
    store.stickInputPrompt = data.stickInputPrompt
    store.speechRecognition = data.speechRecognition
    store.speechRecognitionLang = data.speechRecognitionLang || store.speechRecognitionLang
    store.speechRecognitionAlwaysOn = data.speechRecognitionAlwaysOn
    store.speechRecognitionAutoSend = data.speechRecognitionAutoSend
    store.speechRecognitionPhraseActivation = data.speechRecognitionPhraseActivation
    store.speechRecognitionBeep = data.speechRecognitionBeep
    store.allowAttachments = data.allowAttachments
    store.authToken = data.authToken
    store.disableDayNightMode = data.disableDayNightMode
    store.enableLogout = data.enableLogout
    store.enableResend = data.enableResend
    store.speechSynthesis = data.speechSynthesis
    store.speechSynthesisEnabled = store.speechSynthesisSupported && data.speechSynthesisEnabledByDefault
    store.speechSynthesisPitch = data.speechSynthesisPitch
    store.speechSynthesisRate = data.speechSynthesisRate
    store.speechSynthesisVoices = data.speechSynthesisVoices

    if (store.userId === undefined) {
        store.userId = getUserId()
    }
    store.customIFramedMsgs = data.customIFramedMsgs
    store.initialConversationMetadata = data.initialConversationMetadata
    store.stateOverride = data.stateOverride

    store.fsmDef = data.fsmDef;
    store.title = data.title;
    store.subtitle = data.subtitle;

    store.fullScreen = data.fullScreen
    store.sourcesFirst = data.sourcesFirst
    store.hideSources = data.hideSources
    store.hideToolMessages = data.hideToolMessages

    if (store.fullScreen) {
        store.opened = true
        store.maximized = false
    }
    if (data.startSmallMode) {
        store.maximized = false
    }
    if (data.startWithHistoryClosed) {
        store.historyOpened = false
    }
    if (data.onlyChat) {
        store.noHeader = true;
        store.historyOpened = false;
    }
    if (data.fitToParent) {
        store.opened = true;
        store.fitToParent = true;
    }
    i18n.locale.value = data.lang || "en";
    initialized.value = true;
}

function isPhone() {
    let check = false;
    (function (a) {
        if (/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a) || /1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0, 4))) check = true;
    })(navigator.userAgent || navigator.vendor || window.opera);
    return check;
}

addEventListener("resize", (event) => {
    isPhoneLandscape.value = false;
    if (isPhone()) {
        isPhoneLandscape.value = screen.orientation.type.includes('landscape');
    }
});

onMounted(async () => {
    await init()
    if (screen.width < screen.height)
        store.historyOpened = false
})

</script>

<style lang="scss">
@import "~/assets/styles/global.scss";

$phone-breakpoint: 600px;

.fit-to-parent {
    height: inherit !important;
    min-height: inherit !important;
    border-radius: inherit !important;
}

.chatfaq-widget {
    .widget-wrapper.full-screen > .widget-body > .chat {
        > .conversation-content {
            padding-left: 260px;
            padding-right: 260px;
            @media only screen and (max-width: $phone-breakpoint) {
                padding-left: unset;
                padding-right: unset;
            }
        }

        > .input-chat-wrapper {
            margin-left: 260px;
            margin-right: 260px;
            @media only screen and (max-width: $phone-breakpoint) {
                margin-left: 24px;
                margin-right: 24px;
            }
        }

        &.history {
            > .conversation-content {
                padding-left: 130px;
                padding-right: 130px;
                @media only screen and (max-width: $phone-breakpoint) {
                    padding-left: unset;
                    padding-right: unset;
                }
            }

            > .input-chat-wrapper {
                margin-left: 130px;
                margin-right: 130px;
                @media only screen and (max-width: $phone-breakpoint) {
                    margin-left: 24px;
                    margin-right: 24px;
                }
            }
        }
    }
}
</style>

<style lang="scss" scoped>

$widget-open-button-margin: 24px;
$history-width: 260px;
$history-width-mobile: 260px;
$phone-breakpoint: 600px;
$widget-margin: 16px;

.chatfaq-widget {
    position: fixed;
    &.fit-to-parent {
        position: unset;
    }
    z-index: 1000;
    bottom: 0;
    right: 0;

    .dark-filter {
        display: none;

        position: absolute;
        width: 100dvw;
        height: 100dvh;
        background-color: $chatfaq-color-darkFilter;
        z-index: 1;
        @media only screen and (max-width: $phone-breakpoint) {
            display: unset;
        }
    }

    .widget-history {
        background: $chatfaq-color-menu-background;
        width: $history-width;
        height: 580px;
        border-radius: 10px 0px 0px 10px;
        border-top: 1px solid $chatfaq-color-menu-border;
        border-left: 1px solid $chatfaq-color-menu-border;
        border-bottom: 1px solid $chatfaq-color-menu-border;

        @media only screen and (max-width: $phone-breakpoint) {
            width: $history-width-mobile;
            border-right: 1px solid $chatfaq-color-menu-border;
        }

        &.maximized {
            height: 85dvh;
        }

        &.full-screen {
            height: 100dvh;
            border-radius: unset;
        }
    }

    .widget-wrapper {
        position: absolute;
        display: flex;
        align-items: stretch;
        flex-flow: row;
        right: 0px;
        margin: $widget-margin;

        bottom: calc($chatfaq-size-bubbleButton + $widget-open-button-margin);

        &.fit-to-parent {
            position: unset;
            margin: 0px;
        }
        &.full-screen {
            bottom: 0;
            margin: 0px;
        }

        .widget-body {
            &.fit-to-parent {
                width: 100% !important;
            }
            &.maximized {
                @media only screen and (min-width: $phone-breakpoint) {
                    width: calc(100dvw - $history-width - $widget-margin * 2);
                    height: 85dvh;
                }

                &.history-closed {
                    @media only screen and (min-width: $phone-breakpoint) {
                        width: calc(100dvw - $widget-margin * 2);
                    }
                }
            }

            &.full-screen {
                @media only screen and (min-width: $phone-breakpoint) {
                    width: calc(100dvw - $history-width);
                    height: 100dvh;
                }

                &.history-closed {
                    @media only screen and (min-width: $phone-breakpoint) {
                        width: calc(100dvw);
                    }
                }
            }
            display: flex;
            width: 400px;
            height: 580px;
            align-items: stretch;
            flex-flow: column;
            @media only screen and (max-width: $phone-breakpoint) {
                width: 100%;
                height: 100%;
            }
        }

        @media only screen and (max-width: $phone-breakpoint) {
            height: 100dvh;
            width: 100dvw;
            margin: 0px;
            bottom: 0px;
        }
    }


    .widget-wrapper > .widget-body > .header {
        border: 1px solid $chatfaq-color-menu-border;
        border-radius: 10px 10px 0px 0px;

        &.history {
            border-radius: 0px 10px 0px 0px;

            &.full-screen {
                border-radius: unset;
            }

            @media only screen and (max-width: $phone-breakpoint) {
                border-radius: unset;
            }
        }

        @media only screen and (max-width: $phone-breakpoint) {
            border-radius: unset;
        }

        &.full-screen {
            border-radius: unset;
        }
    }

    .widget-wrapper.full-screen > .widget-body > .chat {
        border-radius: unset;
        @media only screen and (max-width: $phone-breakpoint) {
            padding: unset;
        }

    }

    .widget-wrapper > .widget-body.full-screen > .header {
        border-radius: unset;
    }

    .widget-wrapper > .widget-body > .chat {
        position: relative;
        flex-grow: 1;
        overflow: auto;
        border-left: 1px solid $chatfaq-color-menu-border;
        border-right: 1px solid $chatfaq-color-menu-border;
        border-bottom: 1px solid $chatfaq-color-menu-border;
        border-radius: 0px 0px 10px 10px;
        &.no-header { // No header means no history neither
            border-radius: 10px;
            border-top: 1px solid $chatfaq-color-menu-border;
        }

        &.history {
            border-radius: 0px 0px 10px 0px;

            &.full-screen {
                border-radius: unset;
            }

            @media only screen and (max-width: $phone-breakpoint) {
                border-radius: unset;
            }
        }

        @media only screen and (max-width: $phone-breakpoint) {
            border-radius: unset;
        }
    }

    .widget-open-button {
        cursor: pointer;
        background: $chatfaq-color-bubbleButton-background;

        &:hover {
            background: $chatfaq-color-bubbleButton-background-hover;
        }

        width: $chatfaq-size-bubbleButton;
        height: $chatfaq-size-bubbleButton;
        border-radius: $chatfaq-size-bubbleButton;
        position: absolute;
        bottom: 0px;
        right: 0px;
        margin: $widget-open-button-margin;

        &.opened {
            @media only screen and (max-width: $phone-breakpoint) {
                display: none;
            }
        }

        .bubble-icon {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);

            &.open {
                color: $chatfaq-bubble-button-open-icon-color;
            }
            &.close {
                color: $chatfaq-bubble-button-close-icon-color;
            }
        }
    }

    .not-supported {
        position: absolute;
        bottom: 0px;
        right: 0px;
        margin: $widget-open-button-margin;
    }
}
</style>

