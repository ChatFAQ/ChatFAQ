<template>
    <div class="user-feedback-wrapper">
        <div class="feedback-list" v-if="userFeedback.length">
            <div v-for="feedback in userFeedback" :key="feedback.id" class="feedback-item">
                <div v-if="feedback.feedback_data.thumb_value === 'positive'" class="vote-icon thumb-up"></div>
                <div v-else-if="feedback.feedback_data.thumb_value === 'negative'" class="vote-icon thumb-down"></div>
                <div v-if="feedback.feedback_data.star_rating" class="star-rating">
                    <div class="stars">
                        <div v-for="star in feedback.feedback_data.star_rating_max" :key="star" class="star" :class="{
                            'filled': feedback.feedback_data.star_rating_max - star < feedback.feedback_data.star_rating
                        }">
                            ★
                        </div>
                    </div>
                    <span class="rating-text">{{ feedback.feedback_data.star_rating }}/{{ feedback.feedback_data.star_rating_max }}</span>
                </div>
                <div v-if="feedback.feedback_data.feedback_comment" class="user-feedback">
                    {{ $t("comment:") }} {{ feedback.feedback_data.feedback_comment }}
                </div>
                <div v-if="feedback.feedback_data.feedback_selection && feedback.feedback_data.feedback_selection.length" class="user-feedback">
                    {{$t(". selections:")}} {{ feedback.feedback_data.feedback_selection.join(", ") }}
                </div>
            </div>
        </div>
        <div v-else class="no-feedback">{{ $t("nofeedbackyet") }}</div>
    </div>
</template>

<script setup>
import { useI18n } from "vue-i18n";
import { authHeaders } from "~/store/items.js";

const { $axios } = useNuxtApp()

const { t } = useI18n();
const props = defineProps({
    messageId: {
        type: Number,
        mandatory: true
    },
})
const userFeedback = ref({})
watch(() => props.messageId, async (_) => {
    await initUserFeedback()
}, { immediate: true })

async function initUserFeedback() {
    userFeedback.value = (await $axios.get("/back/api/broker/user-feedback/?message_target=" + props.messageId, { headers: authHeaders() })).data.results
    if (userFeedback.value.length === 0) {
        userFeedback.value = { feedback: t("nofeedbackyet") }
    }
}

</script>

<style lang="scss">
.user-feedback-wrapper {
    display: flex;
    flex-direction: row;
    margin-bottom: 10px;
    align-items: center;

    .user-feedback {
        font-style: italic;
        font-size: 14px;
    }

    .vote-icon {
        width: 16px;
        height: 16px;
        margin-right: 16px;
        margin-top: 5px;
        background-repeat: no-repeat;
        background-position: center;
        padding: 12px;
        border-radius: 2px;
        background-color: #4630751A;

        &.thumb-up {
            background-image: url('~/assets/icons/thumb-up.svg');
        }

        &.thumb-down {
            background-image: url('~/assets/icons/thumb-down.svg');
        }
    }

    .feedback-list {
        display: flex;
        flex-direction: column;
        width: 100%;
    }

    .feedback-item {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        padding: 6px 12px;
        border-radius: 4px;
    }


    .star-rating {
        display: flex;
        align-items: center;
        gap: 8px;

        .stars {
            display: flex;
            flex-direction: row-reverse;
            gap: 4px;
        }

        .star {
            font-size: 20px;
            color: #ddd;

            &.filled {
                color: #FFD700;
            }
        }

        .rating-text {
            font-size: 14px;
            color: #666;
        }
    }

    .user-feedback {
        font-size: 14px;
        line-height: 2.0;
    }
}
</style>
