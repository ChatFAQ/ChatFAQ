<template>
    <div class="labeling-tool-wrapper">
        <div class="back-button-wrapper" >
            <BackButton @click="emit('exit')" class="back-button"/>
            <div class="saving-indicator">
                <div v-if="itemsStore.savingItem">
                    <el-icon>
                        <Refresh/>
                    </el-icon>
                    {{ $t("saving...") }}
                </div>
                <div v-else>
                    <el-icon>
                        <Check/>
                    </el-icon>
                    {{ $t("saved") }}
                </div>
                <div class="number-of-items">{{progressInfo.progress}}/{{progressInfo.total}} {{ $t("items") }}</div>
            </div>
        </div>
        <div class="labeling-tool" v-loading="loadingConversation">
            <div class="labeling-tool-panels">
                <div class="labeling-tool-left-side">
                    <div class="selected-conversation-info">
                        <div>{{conversation.name}}</div>
                        <div>{{ conversation?.fsms ? conversation.fsms.join(",") : "" }}</div>
                        <div>{{formatDate(conversation.created_date)}}</div>
                    </div>
                    <div v-for="msgs in getQAMessageGroups(conversation.msgs_chain)"
                         @click="labeledQAGroup = msgs"
                         class="qa-group"
                         :class="{
                             'selected': (labeledQAGroup !== undefined && labeledQAGroup[labeledQAGroup.length - 1].id === msgs[msgs.length - 1].id),
                             'reviewed': msgs[msgs.length - 1].reviewed
                         }"
                    >
                        <div v-for="(msg, index) in msgs" class="message" :class="{[msg.sender.type]: true, 'hide': !renderableMsg(msg)}" >
                            <span v-if="!index && msgs[msgs.length - 1].reviewed" class="reviewed-check">
                                <el-icon>
                                    <CircleCheck/>
                                </el-icon>
                            </span>
                            <div v-if="renderableMsg(msg)" class="message-content" :class="{[msg.sender.type]: true}">
                                {{
                                    typeof (msg.stack[0].payload) === 'string' ? msg.stack[0].payload : msg.stack[0].payload.content
                                }}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="labeling-tool-right-side">
                    <el-tabs model-value="knowledge-items" class="knowledge-items">
                        <el-tab-pane :lazy="true" :label="$t('knowledgeitems')" name="knowledge-items">
                            <KnowledgeItemReview v-if="labeledQAGroup !== undefined"
                                                 :message="labeledQAGroup[labeledQAGroup.length - 1]"
                                                 :references="referencesQAMessageGroup(labeledQAGroup)"
                                                 ref="kiReviewer"
                            />
                            <div class="no-answer-selected" v-else>{{ $t('selectananswertolabel') }}</div>
                        </el-tab-pane>
                        <el-tab-pane :lazy="true" :label="$t('givefeedback')" name="give-feedback">
                            <GenerationReview v-if="labeledQAGroup !== undefined" :messageId="labeledQAGroup[labeledQAGroup.length - 1].id"/>
                            <div class="no-answer-selected" v-else>{{ $t('selectananswertolabel') }}</div>
                        </el-tab-pane>
                        <el-tab-pane :lazy="true" :label="$t('usersfeedback')" name="users-feedback">
                            <UserFeedback v-if="labeledQAGroup !== undefined" :messageId="labeledQAGroup[labeledQAGroup.length - 1].id"/>
                            <div class="no-answer-selected" v-else>{{ $t('selectananswertolabel') }}</div>
                        </el-tab-pane>
                    </el-tabs>
                </div>
            </div>
            <div class="page-buttons">
                <el-button @click="pageConversation(-1)" :disabled="!thereIsPrev">
                    <el-icon>
                        <ArrowLeft/>
                    </el-icon>
                    <span>{{ $t("previous") }}</span>
                </el-button>
                <el-button @click="pageConversation(1)" :disabled="!thereIsNext">
                    <span>{{ $t("next") }}</span>
                    <el-icon>
                        <ArrowRight/>
                    </el-icon>
                </el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore, authHeaders} from "~/store/items.js";
import KnowledgeItemReview from "~/components/labeling/KnowledgeItemReview.vue";
import BackButton from "~/components/generic/BackButton.vue";
import UserFeedback from "~/components/labeling/UserFeedback.vue";
import GenerationReview from "~/components/labeling/GenerationReview.vue";
import {ArrowLeft, ArrowRight, CircleCheck, Refresh} from "@element-plus/icons-vue";
import {formatDate} from "~/utils";

const itemsStore = useItemsStore()

const router = useRouter()

const {$axios} = useNuxtApp()

const labeledQAGroup = ref(undefined)
const progressInfo = ref({"progress": 0, "total": 0})

const props = defineProps({
    id: {
        type: String,
        mandatory: true
    },
})
const emit = defineEmits(["exit"])
const itemId = ref(props.id)
const review = ref({data: []})
const kiReviewer = ref(null)
const conversation = ref({})
const loadingConversation = ref(false)
const thereIsNext = ref(true)
const thereIsPrev = ref(true)
let conversations = []
// get conversation async data
async function initConversation() {
    loadingConversation.value = true
    conversation.value = (await $axios.get("/back/api/broker/conversations/" + itemId.value + "/")).data
    conversations = await itemsStore.retrieveItems("/back/api/broker/conversations/")
    thereIsNext.value = (await itemsStore.getNextItem(conversations, "/back/api/broker/conversations/", itemId.value, 1)) !== undefined
    thereIsPrev.value = (await itemsStore.getNextItem(conversations, "/back/api/broker/conversations/", itemId.value, -1)) !== undefined
    progressInfo.value = (await $axios.get("/back/api/broker/conversations/" + itemId.value + "/review_progress/", { headers: authHeaders() })).data
    loadingConversation.value = false
}

await initConversation()
watch(() => props.id, async () => {
    itemId.value = props.id
}, {immediate: true})
watch(() => itemsStore.savingItem, async () => {
    await initConversation()
}, {immediate: true})
watch(itemId, async () => {
    await initConversation()
    selectFirstMessage()
}, {immediate: true})

function getQAMessageGroups(MMLChain) {

    let groups = []
    let group = []
    if (!MMLChain)
        return groups
/*    for (let i = 0; i < MMLChain.length; i++) {
        if (MMLChain[i].sender.type === 'bot') {
            group.push(MMLChain[i])
            groups.push(group)
            group = []
        } else {
            group.push(MMLChain[i])
        }
    }
 */
    // If the MMLChain is like this [b, h, b, b, b, h, b, h, b, h, b, b]
    // we should return [[b], [h, b, b, b, b], [h, b], [h, b], [h, b, b]]
    // so that the first message of each group is a human message (in case a bot message is not the first of the conversation)
    let i = 0
    while (i < MMLChain.length) {
        if (MMLChain[i].sender.type === 'human') {
            group.push(MMLChain[i])
            i++
            while (i < MMLChain.length && MMLChain[i].sender.type === 'bot') {
                group.push(MMLChain[i])
                i++
            }
            groups.push(group)
            group = []
        } else {
            group.push(MMLChain[i])
            i++
        }
    }
  return groups
}

async function pageConversation(direction) {
    loadingConversation.value = true
    labeledQAGroup.value = undefined
    const nextItem = await itemsStore.getNextItem(conversations, "/back/api/broker/conversations/", itemId.value, direction)
    if (nextItem !== undefined) {
        itemId.value = nextItem.id
    }
    loadingConversation.value = false
}
function selectFirstMessage() {
    const qas = getQAMessageGroups(conversation.value.msgs_chain)
    if (qas?.length)
        labeledQAGroup.value = qas[0]
}
function referencesQAMessageGroup(msgsGroup) {
    let references = {}

    for (const msg of msgsGroup) {
        // msg.stack[i...n].payload.references are a dict,obj
        for (const stack of msg.stack || []) {
            if (stack.payload.references) {
                references = {...references, ...stack.payload.references}
            }
        }
    }
    return references
}
function renderableMsg(msg) {
    return msg.stack && msg.stack.length
}
</script>

<style lang="scss">
.labeling-tool-wrapper {
    .el-tabs__nav  {
        margin-top: 16px !important;
    }
    .labeling-tool {
        .el-tabs {
            margin-left: 24px;
            margin-right: 24px;
            display: flex;
            flex-direction: column;
            height: 100%;

            .el-tabs__content {
                height: 100%;
                overflow-y: auto;

                .el-tab-pane {
                    height: 100%;
                }
            }
        }

        .el-tabs__nav {
            float: unset;
        }

        .el-tabs__header {
            margin-bottom: 24px;
        }
    }
    .no-answer-selected {
        margin-bottom: 8px;
        font-style: italic;
        font-size: 14px;
    }
}
</style>
<style lang="scss" scoped>

.labeling-tool-wrapper {
    padding-left: 60px;
    .labeling-tool {
        display: flex;
        flex-direction: column;
        margin-right: 60px;
        .labeling-tool-panels {
            display: flex;
            flex-direction: row;
            height: 70vh;
            .labeling-tool-left-side, .labeling-tool-right-side {
                border-radius: 10px;
                background: white;
                border: 1px solid $chatfaq-color-primary-200;
                overflow-y: auto;
            }

            .labeling-tool-left-side {
                flex: 1.75;
                margin-right: 12px;
            }

            .labeling-tool-right-side {
                flex: 1.25;
                margin-left: 12px;
                display: flex;
                flex-direction: column;
            }

            .qa-group {
                position: relative;
                padding: 16px;

                &:hover {
                    background: rgba(223, 218, 234, 0.49);
                    cursor: pointer;
                }

                &.selected {
                    background: $chatfaq-color-primary-200;
                }

                .message {
                    width: 100%;

                    display: block;
                    &.hide {
                        display: none;
                    }
                    overflow: auto;

                    .message-content {
                        max-width: 90%;
                        border-radius: 6px;
                        padding: 8px 12px 8px 12px;
                        margin-bottom: 8px;
                        overflow-wrap: break-word;

                        &.bot {
                            float: left;
                            background: #46307524;
                        }

                        &.human {
                            background: $chatfaq-color-primary-500;
                            float: right;
                            color: white;
                        }
                    }
                }
            }
        }

        .qa-group.reviewed:not(.selected) {
            .message-content.bot {
                background: #edebf2;
            }

            .message-content.human {
                background: #7e6e9c;
            }
        }

        .knowledge-items {
            // height: calc(100% - 70px);
            height: 100%;
        }

        .labeling-ki-commands {
            height: 70px;
            width: 100%;
            display: flex;
            justify-content: space-between;
            text-align: center;
            align-items: center;
            padding: 24px;
            border-top: 1px solid $chatfaq-color-primary-200;
        }

        .clear-command {
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            color: $chatfaq-color-primary-500;

        }

        .command {
            padding: 20px 20px 20px 20px;
            width: 80px;
            border-radius: 8px !important;
            text-transform: uppercase !important;
        }

        .cancel-command {
            border-color: $chatfaq-color-primary-500;
            color: $chatfaq-color-primary-500;
        }

        .save-command {
            background-color: #463075;
            color: white;
        }
    }

    .back-button-wrapper {
        display: flex;
        justify-content: space-between;

        .back-button {
            margin-top: 26px;
            margin-bottom: 26px;
        }

        .saving-indicator {
            display: flex;
            cursor: pointer;
            align-items: center;
            font-size: 12px;
            color: $chatfaq-color-greyscale-800;
            margin-right: 80px;

            i {
                margin-right: 8px;
            }

            > :first-child {
                margin-right: 32px;
            }
        }

        .number-of-items {

        }
    }

    .reviewed-check {
        color: $chatfaq-color-primary-500;

        i {
            margin-top: 10px;
        }
    }

    .page-buttons {
        display: flex;
        justify-content: center;
        margin-top: 32px;

        button {
            @include button-round;

            &:first-child {
                margin-right: 16px;

                i {
                    margin-right: -2px;
                }
            }

            &:last-child {
                i {
                    margin-left: 4px;
                }
            }
        }
    }

    .selected-conversation-info {
        font-size: 12px;
        font-weight: 400;
        line-height: 18px;
        letter-spacing: 0;

        background-color: white;
        width: 100%;
        z-index: 1;
        position: sticky;
        top: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
        text-align: center;
        padding-bottom: 16px;
        padding-top: 16px;
        color: #545A64;

    }
}
</style>

