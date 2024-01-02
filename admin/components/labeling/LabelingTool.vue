<template>
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
            <el-tabs model-value="knowledge-items">
                <el-tab-pane :lazy="true" :label="$t('knowledgeitems')" name="knowledge-items">
                    <div v-if="labelingKnowledgeItems.message_id !== undefined" v-loading="itemsStore.loading" class="labeling-kis-wrapper">
                        <div v-for="ki in labelingKnowledgeItems.kis" class="labeling-ki-wrapper">
                            <div class="ki-vote">
                                <div
                                    class="vote-icon thumb-up"
                                    @click="voteKI(labelingKnowledgeItems.message_id, ki.id, 'positive')"
                                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'positive'}"
                                ></div>
                                <div
                                    class="vote-icon thumb-down"
                                    @click="voteKI(labelingKnowledgeItems.message_id, ki.id, 'negative')"
                                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'negative'}"
                                ></div>
                            </div>
                            <div class="labeling-ki">
                                <div class="ki-title">{{ ki.title }}</div>
                                <div class="ki-content">{{ ki.content }}</div>
                            </div>
                        </div>
                        <div>Alternative knowledge item</div>
                        <div @click="addAlternativeKI(labelingKnowledgeItems.message_id)">+ Add knowledge item</div>
                        <div v-for="ki in alternativeKIs(labelingKnowledgeItems.message_id)" class="labeling-ki-wrapper">
                            <el-select v-model="ki.knowledge_item_id">
                                <el-option
                                    v-for="choice in [{'title': 'aaaa', 'id': 1}, {'title': 'bbb', 'id': 2}, {'title': 'ccc', 'id': 3}]"
                                    :key="choice.id"
                                    :label="choice.title"
                                    :value="choice.id"
                                />
                            </el-select>
                        </div>
                        <div class="labeling-ki-commands">
                            <el-button>Clear</el-button>
                            <el-button>Cancel</el-button>
                            <el-button @click="sendReviews(labelingKnowledgeItems.message_id)">Save</el-button>
                        </div>
                    </div>
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('givefeedback')" name="give-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
                <el-tab-pane :lazy="true" :label="$t('usersfeedback')" name="users-feedback">
                    {{ msgLabeled }}
                </el-tab-pane>
            </el-tabs>
        </div>
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const router = useRouter()

const {$axios} = useNuxtApp()

const msgLabeled = ref(undefined)

const labelingKnowledgeItems = ref({})
const review = ref({
    value: []
})

const props = defineProps({
    id: {
        type: String,
        mandatory: true
    },
})

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
    labelingKnowledgeItems.value = {message_id: botMsg.id, kis: []}
    for (const reference of botMsg.stack[botMsg.stack.length - 1].payload.references) {
        const ki = await itemsStore.requestOrGetItem($axios, "/back/api/language-model/knowledge-items/", {
            id: reference.knowledge_item_id
        })
        if (ki)
            labelingKnowledgeItems.value.kis.push(ki)
    }
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: botMsg.id}) || {}
    msgLabeled.value = QAPair
    itemsStore.loading = false
}
async function voteKI(messageId, kiId, vote) {
    if (review?.value?.data === undefined) {
        review.value = {
            data: []
        }
    }
    const data = getVoteKI(kiId)
    if (data) {
        data.value = vote
    } else {
        review.value.data.push({
            value: vote,
            knowledge_item_id: kiId,
        })
    }
    await sendReviews(messageId)
}
async function sendReviews(messageId) {
    review.value.message = messageId
    review.value.data = review.value.data.filter((d) => d.knowledge_item_id !== null)
    if (review.value.id === undefined) {
        await $axios.post("/back/api/broker/admin-review/", review.value)
    } else {
        await $axios.put("/back/api/broker/admin-review/" + review.value.id + "/", review.value)
    }
}
function getVoteKI(kiId) {
    if (review.value.id === undefined) {
        return undefined
    } else {
        // first get the data[i] if exists any knowledge_item_id == kiId
        return review.value.data.find((d) => d?.knowledge_item_id && d.knowledge_item_id.toString() === kiId.toString())
    }
}
function addAlternativeKI(messageId) {
    if (review?.value?.data === undefined) {
        review.value = {
            data: []
        }
    }
    return review.value.data.push({
        value: "alternative",
        knowledge_item_id: null,
    })
}
function alternativeKIs() {
    return review?.value?.data?.filter((d) => d.value === "alternative") || []
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

    .labeling-kis-wrapper {
        height: 100%;

        .labeling-ki-wrapper {
            display: flex;

            .ki-vote {
                display: flex;

                .vote-icon {
                    width: 16px;
                    height: 16px;
                    margin-right: 16px;
                    margin-top: 5px;
                    cursor: pointer;
                    background-repeat: no-repeat;
                    background-position: center;
                    padding: 12px;
                    border-radius: 2px;

                    &.thumb-up {
                        background-image: url('~/assets/icons/thumb-up.svg');
                    }
                    &.thumb-down {
                        background-image: url('~/assets/icons/thumb-down.svg');
                    }
                    &.selected {
                        background-color: #4630751A;
                    }

                }
            }

            .ki-title {
                color: #463075;
                font-size: 14px;
                font-weight: 600;
                line-height: 20px;
                margin-bottom: 8px;
            }

            .ki-content {
                text-overflow: ellipsis;
                overflow: hidden;
                height: 4.0em;
            }

            .labeling-ki {
                padding: 8px 16px 8px 16px;
                border: 1px solid $chatfaq-color-primary-200;
                background: #DFDAEA66;
                border-radius: 4px;
                margin-bottom: 16px;
                margin-right: 24px;
            }
        }
    }
}
</style>

