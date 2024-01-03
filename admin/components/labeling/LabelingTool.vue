<template>
    <BackButton class="back-button-wrapper"/>
    <div class="labeling-tool-wrapper">
        <div class="labeling-tool-left-side">
            <div @click="setQAPairToLabel(msgs)"
                 v-for="msgs in getQAMessageGroups(conversation.mml_chain)" class="qa-group">
                <div v-for="msg in msgs" class="message" :class="{[msg.sender.type]: true}">
                    <div class="message-content" :class="{[msg.sender.type]: true}">
                        {{
                            typeof (msg.stack[0].payload) === 'string' ? msg.stack[0].payload : msg.stack[0].payload.model_response
                        }}
                    </div>
                </div>
            </div>
        </div>
        <div class="labeling-tool-right-side">
            <el-tabs model-value="knowledge-items" class="knowledge-items">
                <el-tab-pane :lazy="true" :label="$t('knowledgeitems')" name="knowledge-items">
                    <KnowledgeItemReview :referencedKnowledgeItems="referencedKnowledgeItems"
                                         :referencedKnowledgeBaseId="referencedKnowledgeBaseId"
                                         :review="review"
                                         ref="kiReviewer"
                    />
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('givefeedback')" name="give-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('usersfeedback')" name="users-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
            </el-tabs>
            <div class="labeling-ki-commands">
                <div class="clear-command" @click="kiReviewer.clear()">Clear</div>
                <div>
                    <el-button class="cancel-command command" @click="itemsStore.editing = undefined">Cancel</el-button>
                    <el-button class="save-command command" @click="kiReviewer.save()">Save</el-button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import KnowledgeItemReview from "~/components/labeling/KnowledgeItemReview.vue";
import BackButton from "~/components/generic/BackButton.vue";

const itemsStore = useItemsStore()

const router = useRouter()

const {$axios} = useNuxtApp()

const msgLabeled = ref(undefined)

const props = defineProps({
    id: {
        type: String,
        mandatory: true
    },
})

const referencedKnowledgeBaseId = ref(undefined)
const referencedKnowledgeItems = ref({})
const review = ref({data: []})
const kiReviewer = ref(null)

// get conversation async data
const {data} = await useAsyncData(
    "conversation" + props.id,
    async () => await $axios.get("/back/api/broker/conversations/" + props.id + "/")
)

const conversation = ref(data.value.data)

function getQAMessageGroups(MMLChain) {
    let groups = []
    let group = []
    for (let i = 0; i < MMLChain.length; i++) {
        if (MMLChain[i].sender.type === 'bot') {
            group.push(MMLChain[i])
            groups.push(group)
            group = []
        } else {
            group.push(MMLChain[i])
        }
    }
    return groups
}

async function setQAPairToLabel(QAPair) {
    itemsStore.loading = true
    const botMsg = QAPair[QAPair.length - 1]
    referencedKnowledgeItems.value = {message_id: botMsg.id, kis: []}
    referencedKnowledgeBaseId.value = botMsg.stack[botMsg.stack.length - 1].payload.references.knowledge_base_id
    for (const reference of botMsg.stack[botMsg.stack.length - 1].payload.references.knowledge_items) {
        const ki = await itemsStore.requestOrGetItem($axios, "/back/api/language-model/knowledge-items/", {
            id: reference.knowledge_item_id
        })
        if (ki)
            referencedKnowledgeItems.value.kis.push(ki)
    }
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: botMsg.id}) || {}
    msgLabeled.value = QAPair
    itemsStore.loading = false
}
</script>

<style lang="scss">
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
    justify-content: space-between;
}

.el-tabs__header {
    margin-bottom: 24px;
}
</style>
<style lang="scss" scoped>
.labeling-tool-wrapper {
    display: flex;
    flex-direction: row;
    margin-right: 60px;

    .labeling-tool-left-side, .labeling-tool-right-side {
        border-radius: 10px;
        background: white;
        border: 1px solid $chatfaq-color-primary-200;
        max-height: 70vh;
        overflow-y: auto;
        padding-top: 16px;
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
        padding: 16px 12px;

        &:hover {
            background: $chatfaq-color-primary-200;
            cursor: pointer;
        }

        .message {
            width: 100%;

            display: block;
            overflow: auto;

            .message-content {
                max-width: 428px;
                border-radius: 6px;
                padding: 8px 12px 8px 12px;
                margin-bottom: 8px;
                overflow-wrap: break-word;

                &.bot {
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

    .knowledge-items {
        height: calc(100% - 70px);
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
    margin-top: 26px;
    margin-bottom: 26px;
}
</style>

