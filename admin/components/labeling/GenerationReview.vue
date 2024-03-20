<template>
    <div class="generation-review-wrapper"  v-loading="itemsStore.loading"  element-loading-background="rgba(255, 255, 255, 0.8)">
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
            class="review-message"
            v-model="review.gen_review_msg"
            type="textarea"
            @keydown.enter.stop
            :placeholder="$t('giveanalternativeanswer')"
            :autosize="{ minRows: 3 }"
            @input="submitReviewMsg"
        />
    </div>
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";
import { upsertItem } from "~/utils/index.js";
import {useI18n} from "vue-i18n";

const { t } = useI18n();

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

let reviewMsgSaveTimeout = undefined

watch(() => props.messageId, async (_) => {
    await initGenReview()
}, {immediate: true})

async function initGenReview() {
    itemsStore.loading = true
    review.value = await itemsStore.retrieveItems("/back/api/broker/admin-review/", {message: props.messageId, limit: 0, offset: 0, ordering: undefined}, true) || {}
    reviewType.value = review.value.gen_review_type
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
    // deep copy review.value
    const _review = JSON.parse(JSON.stringify(review.value))
    delete _review.ki_review_data
    _review.message = props.messageId
    await upsertItem("/back/api/broker/admin-review/", _review, itemsStore, true, {limit: 0, offset: 0, ordering: undefined}, t)

}
async function submitReviewMsg(val) {
    itemsStore.savingItem = true
    review.value.gen_review_msg = val
    // Because this is an input field and might trigger too many saves, we save only when the user stops typing:
    if (reviewMsgSaveTimeout) {
        clearTimeout(reviewMsgSaveTimeout);
        reviewMsgSaveTimeout = undefined
    }
    reviewMsgSaveTimeout = setTimeout(async () => {
        await save()
    }, 1000)
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
    .review-message {
        textarea {
            color: $chatfaq-color-neutral-black;
            border-radius: 8px;
        }
    }
}
</style>
