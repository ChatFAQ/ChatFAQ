<template>
    <Suspense>
        <div class="chatfaq-widget">
            <div v-if="isPhoneLandscape" class="not-supported">
                <div class="not-supported-text">
                    <div class="not-supported-text-title">Sorry, we don't support mobile landscape mode yet.</div>
                    <div class="not-supported-text-subtitle">Please, turn your phone to portrait mode.</div>
                </div>
            </div>
            <div v-if="store.opened && !isPhoneLandscape" class="widget-wrapper"
                 :class="{'history': store.historyOpened, 'full-screen': store.fullScreen}">
                <div class="dark-filter" v-if="store.historyOpened"></div>
                <LeftMenu v-if="store.historyOpened" class="widget-history"
                          :class="{'maximized': store.maximized, 'full-screen': store.fullScreen}"/>
                <div class="widget-body"
                     :class="{'maximized': store.maximized, 'full-screen': store.fullScreen, 'history-closed': !store.historyOpened}">
                    <Header class="header" :class="{'history': store.historyOpened, 'full-screen': store.fullScreen}"/>
                    <Chat class="chat" :class="{'history': store.historyOpened, 'full-screen': store.fullScreen}"/>
                </div>
            </div>
            <div v-if="!isPhoneLandscape && !fullScreen" class="widget-open-button" :class="{'opened': store.opened}"
                 @click="store.opened = !store.opened">
                <i :class="store.opened ? 'close' : 'open'"/>
            </div>
        </div>
    </Suspense>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import { useHead } from "@unhead/vue";
import {ref, defineProps, onMounted} from "vue";
import LeftMenu from "~/components/left-menu/LeftMenu.vue";
import Header from "~/components/chat/Header.vue";
import Chat from "~/components/chat/Chat.vue";
import {getUserId} from "~/utils";

const store = useGlobalStore();
const isPhoneLandscape = ref(false);

useHead({
    meta: [
        {name: 'maximum-scale', content: 1}
    ],
})

const props = defineProps([
    "chatfaqWs",
    "chatfaqApi",
    "fsmDef",
    "userId",
    "manageUserId",
    "title",
    "subtitle",
    "maximized",
    "fullScreen",
    "historyOpened",
    "widgetConfigId"
]);
let data = props
if (props.widgetConfigId !== undefined) {
    const response = await fetch(props.chatfaqApi + `/back/api/widget/widgets/${props.widgetConfigId}/`)
    data = await response.json();
    // sneak case data keys to lowerCamelCase:
    data = Object.keys(data).reduce((acc, key) => {
        acc[key.replace(/_([a-z])/g, (g) => g[1].toUpperCase())] = data[key];
        return acc;
    }, {});

    const style = document.createElement('style');
    style.innerHTML = data.css;
    document.head.appendChild(style);
    console.log(style)
}

store.chatfaqWS = props.chatfaqWs;
store.chatfaqAPI = props.chatfaqApi;
store.userId = props.userId;

if (!store.userId && data.manageUserId) {
    store.userId = getUserId()
}

store.fsmDef = data.fsmDef;
store.title = data.title;
store.subtitle = data.subtitle;


if (data.fullScreen !== undefined)
    store.fullScreen = data.fullScreen;
if (data.maximized !== undefined)
    store.maximized = data.maximized;
if (data.historyOpened !== undefined)
    store.historyOpened = data.historyOpened;

if (store.fullScreen) {
    store.opened = true
    store.maximized = false
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

onMounted(() => {
    if (screen.width < screen.height)
        store.historyOpened = false
})

</script>

<style lang="scss">
@import "~/assets/styles/global.scss";

$phone-breakpoint: 600px;

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

        &.full-screen {
            bottom: 0;
            margin: 0px;
        }

        .widget-body {
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
        height: 100%;
        border-left: 1px solid $chatfaq-color-menu-border;
        border-right: 1px solid $chatfaq-color-menu-border;
        border-bottom: 1px solid $chatfaq-color-menu-border;
        border-radius: 0px 0px 10px 10px;

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

        i {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);

            &.open {
                content: $chatfaq-bubble-button-open-icon;
            }

            &.close {
                content: $chatfaq-bubble-button-close-icon;
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

