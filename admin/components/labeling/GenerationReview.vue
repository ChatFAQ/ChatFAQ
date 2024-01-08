<template>
    <div class="generation-review-wrapper">
        <div class="title-instruction">Rating</div>
        <div class="content-instruction">Read the guidelines in order to rate accordingly</div>
        <div class="rating-wrapper">
            <div class="rating">1</div>
            <div class="rating">2</div>
            <div class="rating">3</div>
            <div class="rating">4</div>
            <div class="rating">5</div>
        </div>
        <div class="title-feedback">Feedback</div>
        <el-select class="select-feedback-type" v-model="reviewType">
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
const {$axios} = useNuxtApp()

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
})

async function initGenReview() {
    review.value = await itemsStore.requestOrGetItem($axios, "/back/api/broker/admin-review/", {message: props.message.id}) || {}
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
            border: 1px solid $chatfaq-color-primary-200;
            border-radius: 24px;
            text-align: center;
            font-size: 14px;
            font-weight: 600;
            color: $chatfaq-color-primary-500;

        }
    }
    .select-feedback-type {
        margin-bottom: 8px;
    }
}
</style>
