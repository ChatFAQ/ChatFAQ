<template>
    <div v-if="reviewedKIs.message_id !== undefined" v-loading="itemsStore.loading"
         class="labeling-kis-wrapper">
        <div v-for="ki in reviewedKIs.kis" class="labeling-ki-wrapper">
            <div class="ki-vote">
                <div
                    class="vote-icon thumb-up"
                    @click="voteKI(ki.id, 'positive')"
                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'positive'}"
                ></div>
                <div
                    class="vote-icon thumb-down"
                    @click="voteKI(ki.id, 'negative')"
                    :class="{selected: getVoteKI(ki.id) && getVoteKI(ki.id).value === 'negative'}"
                ></div>
            </div>
            <div class="labeling-ki">
                <div class="ki-title">{{ ki.title }}</div>
                <div class="ki-content">{{ ki.content }}</div>
            </div>
        </div>
        <div v-if="!itemsStore.loading" class="ki-title add-command-title">Alternative knowledge item</div>
        <div v-if="!itemsStore.loading" v-for="alt2Title in alternatives2Titles" class="alternative-wrapper">
            <el-select v-model="alt2Title[0]" @change="(val) => alternativeChanged(alt2Title[1], val)">
                <el-option
                    v-for="choice in ki_choices"
                    :key="choice.id"
                    :label="choice.title"
                    :value="choice.id"
                />
            </el-select>
        </div>
        <div v-if="!itemsStore.loading" class="ki-title add-command" @click="addAlternativeKI()">+ Add knowledge item</div>
    </div>
</template>


<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const {$axios} = useNuxtApp()

const ki_choices = ref([])
const reviewedKIs = ref({})
const review = ref({})

const props = defineProps({
    message: {
        type: Object,
        mandatory: true
    },
})
watch(() => props.message, async (_) => {
    await initKIReview()
}, {immediate: true})

async function initKIReview() {
    itemsStore.loading = true
    reviewedKIs.value = {message_id: props.message.id, kis: []}
    const references = props.message.stack[props.message.stack.length - 1].payload.references
    for (const ki_ref of references.knowledge_items) {
        const ki = await itemsStore.requestOrGetItem($axios, "/back/api/language-model/knowledge-items/", {
            id: ki_ref.knowledge_item_id
        })
        if (ki)
            reviewedKIs.value.kis.push(ki)
    }
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: props.message.id}) || {}
    ki_choices.value = await itemsStore.requestOrGetItems($axios, "/back/api/language-model/knowledge-items/", {
        knowledge_base: references.knowledge_base_id
    })
    itemsStore.loading = false
}

const alternatives2Titles = computed(() => {
    const res = []
    for (const alt of alternativeKIs()) {
        if (!alt.knowledge_item_id) {
            res.push([undefined, alt])
            continue
        }
        for (const ki of ki_choices.value) {
            if (ki.id.toString() === alt.knowledge_item_id.toString()) {
                res.push([ki.title, alt])
                break
            }
        }
    }
    return res
})

async function voteKI(kiId, vote) {
    if (review.value?.ki_review_data === undefined) {
        review.value = {
            ki_review_data: []
        }
    }
    const data = getVoteKI(kiId)
    if (data) {
        if(data.value === vote)
            data.value = null
        else
            data.value = vote
    } else {
        review.value.ki_review_data.push({
            value: vote,
            knowledge_item_id: kiId,
        })
    }
    await save()
}

async function save() {
    review.value.message = reviewedKIs.value.message_id
    review.value.ki_review_data = review.value.ki_review_data.filter((d) => d.knowledge_item_id !== null)
    // deep copy review.value
    const _review = JSON.parse(JSON.stringify(review.value))
    delete _review.gen_review_msg
    delete _review.gen_review_val
    delete _review.gen_review_type
    await itemsStore.upsertItem($axios, "/back/api/broker/admin-review/", _review)
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: props.message.id}) || {}
}

function getVoteKI(kiId) {
    if (review.value.id === undefined) {
        return undefined
    } else {
        return review.value.ki_review_data.find((d) => d?.knowledge_item_id && d.knowledge_item_id.toString() === kiId.toString())
    }
}

function addAlternativeKI() {
    if (review.value?.ki_review_data === undefined) {
        review.value = {
            ki_review_data: []
        }
    }
    return review.value.ki_review_data.push({
        value: "alternative",
        knowledge_item_id: null,
    })
}
async function alternativeChanged(alt, val) {
    alt.knowledge_item_id = val
    await save()
}
function alternativeKIs() {
    return review.value?.ki_review_data?.filter((d) => d.value === "alternative") || []
}

function clear() {
    review.value = {
        ki_review_data: []
    }
}

defineExpose({
    clear,
    save
})
</script>

<style lang="scss">
.el-select {
    width: 100%;
    margin-right: 24px;
}
</style>
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

    .ki-title {
        color: #463075;
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        margin-bottom: 8px;
    }

    .alternative-wrapper {
        margin-bottom: 16px;
        margin-right: 24px;

        .add-command-title {
            margin-bottom: 8px;
        }
    }
    .add-command {
        margin-top: 16px;
        margin-bottom: 16px;
        cursor: pointer;
    }
}
</style>
