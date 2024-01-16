<template>
    <div class="generation-review-wrapper">
        <div class="title-instruction">Rating</div>
        <div class="content-instruction">Read the guidelines in order to rate accordingly</div>
        <div class="rating-wrapper">
            <div class="rating" @click="setRate(0)" :class="{'selected': review.gen_review_val === 0}">1</div>
            <div class="rating" @click="setRate(1)" :class="{'selected': review.gen_review_val === 1}">2</div>
            <div class="rating" @click="setRate(2)" :class="{'selected': review.gen_review_val === 2}">3</div>
            <div class="rating" @click="setRate(3)" :class="{'selected': review.gen_review_val === 3}">4</div>
            <div class="rating" @click="setRate(4)" :class="{'selected': review.gen_review_val === 4}">5</div>
        </div>
        <div class="title-feedback">Feedback</div>
        <el-select class="select-feedback-type" v-model="reviewType" @change="setReviewType">
            <el-option
                v-for="choice in [{id: 'alternative_answer', label: 'Alternative Answer'}, {id: 'review', label: 'Review'}]"
                :key="choice.id"
                :value="choice.id"
                :label="choice.label"
            />
        </el-select>
        <el-input
            v-model="review.gen_review_msg"
            type="textarea"
            :placeholder="$t('giveanalternativeanswer')"
            :autosize="{ minRows: 3 }"
        />
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const {$axios} = useNuxtApp()
const rate = ref()
const props = defineProps({
    messageId: {
        type: Number,
        mandatory: true
    },
})
const review = ref({})
const reviewType = ref(undefined)

watch(() => props.messageId, async (_) => {
    await initGenReview()
}, {immediate: true})

async function initGenReview() {
    itemsStore.loading = true
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: props.messageId}) || {}
    itemsStore.loading = false
}

async function setRate(val) {
    review.value.gen_review_val = val
    await save()
}
async function setReviewType(val) {
    review.value.gen_review_type = val
    await save()
}

async function save() {
    delete review.value.ki_review_data
    await itemsStore.upsertItem($axios, "/back/api/broker/admin-review/", review.value)
}

</script>

<style lang="scss">
.generation-review-wrapper {
    .title-instruction, .title-feedback {
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        text-align: left;
        color: $chatfaq-color-primary-500;
    }
    .title-feedback {
        margin-bottom: 8px;
    }
    .content-instruction {
        font-size: 12px;
        font-weight: 400;
        text-align: left;
        line-height: 20px;
        color: #8E959F;
        margin-bottom: 16px;
    }
    .rating-wrapper {
        display: flex;
        margin-bottom: 32px;

        .rating  {
            margin-right: 16px;
            height: 24px;
            width: 24px;
            border: 1px solid $chatfaq-color-primary-500;
            border-radius: 24px;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: $chatfaq-color-primary-500;
            cursor: pointer;
            line-height: 21px;
            &.selected {
                background-color: rgba(70, 48, 117, 0.3);
            }

        }
    }
    .select-feedback-type {
        margin-bottom: 8px;
    }
}
</style>
