<template>
    <div v-if="referencedKnowledgeItems.message_id !== undefined" v-loading="itemsStore.loading" class="labeling-kis-wrapper">
        <div v-for="ki in referencedKnowledgeItems.kis" class="labeling-ki-wrapper">
            <div class="ki-vote">
                <div
                    class="vote-icon thumb-up"
                    @click="voteKI(referencedKnowledgeItems.message_id, ki.id, 'positive')"
                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'positive'}"
                ></div>
                <div
                    class="vote-icon thumb-down"
                    @click="voteKI(referencedKnowledgeItems.message_id, ki.id, 'negative')"
                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'negative'}"
                ></div>
            </div>
            <div class="labeling-ki">
                <div class="ki-title">{{ ki.title }}</div>
                <div class="ki-content">{{ ki.content }}</div>
            </div>
        </div>
        <div>Alternative knowledge item</div>
        <div @click="addAlternativeKI(referencedKnowledgeItems.message_id)">+ Add knowledge item</div>
        <div v-for="ki in alternativeKIs(referencedKnowledgeItems.message_id)" class="labeling-ki-wrapper">
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
            <el-button @click="sendReviews(referencedKnowledgeItems.message_id)">Save</el-button>
        </div>
    </div>
</template>


<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const {$axios} = useNuxtApp()

const props = defineProps({
    referencedKnowledgeItems: {
        type: Object,
        default: {},
    },
    review: {
        type: Object,
        default: {data: []},
    },
})
const reviewWriter = ref({...props.review})
watch(() => props.review, (newVal) => {
    reviewWriter.value = {...newVal}
})

async function voteKI(messageId, kiId, vote) {
    if (reviewWriter.value?.data === undefined) {
        reviewWriter.value = {
            data: []
        }
    }
    const data = getVoteKI(kiId)
    if (data) {
        data.value = vote
    } else {
        reviewWriter.value.data.push({
            value: vote,
            knowledge_item_id: kiId,
        })
    }
    await sendReviews(messageId)
}
async function sendReviews(messageId) {
    reviewWriter.value.message = messageId
    reviewWriter.value.data = reviewWriter.value.data.filter((d) => d.knowledge_item_id !== null)
    if (reviewWriter.value.id === undefined) {
        await $axios.post("/back/api/broker/admin-review/", reviewWriter.value)
    } else {
        await $axios.put("/back/api/broker/admin-review/" + reviewWriter.value.id + "/", reviewWriter.value)
    }
}
function getVoteKI(kiId) {
    if (reviewWriter.value.id === undefined) {
        return undefined
    } else {
        return reviewWriter.value.data.find((d) => d?.knowledge_item_id && d.knowledge_item_id.toString() === kiId.toString())
    }
}
function addAlternativeKI(messageId) {
    if (reviewWriter.value?.data === undefined) {
        reviewWriter.value = {
            data: []
        }
    }
    return reviewWriter.value.data.push({
        value: "alternative",
        knowledge_item_id: null,
    })
}
function alternativeKIs() {
    return reviewWriter.value?.data?.filter((d) => d.value === "alternative") || []
}
</script>

<style lang="scss" scoped>
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
</style>
