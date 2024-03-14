<template>
    <div class="user-feedback-wrapper">
        <div v-if="userFeedback.value === 'positive'" class="vote-icon thumb-up"></div>
        <div v-else-if="userFeedback.value === 'negative'" class="vote-icon thumb-down"></div>
        <div class="user-feedback">{{ userFeedback.feedback }}</div>
    </div>
</template>

<script setup>
import {useI18n} from "vue-i18n";
import {authHeaders} from "~/store/items.js";

const {$axios} = useNuxtApp()

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
}, {immediate: true})

async function initUserFeedback() {
    userFeedback.value = (await $axios.get("/back/api/broker/user-feedback/?message=" + props.messageId, {headers: authHeaders()})).data.results
    if (userFeedback.value.length > 0) {
        userFeedback.value = userFeedback.value[0]
    } else {
        userFeedback.value = {feedback: t("nofeedbackyet")}
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
}
</style>
