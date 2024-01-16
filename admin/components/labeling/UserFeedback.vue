<template>
    <div class="user-feedback-wrapper">
        <div v-if="userFeedback.value === 'positive'" class="vote-icon thumb-up"></div>
        <div v-else-if="userFeedback.value === 'negative'" class="vote-icon thumb-down"></div>
        <div class="user-feedback">{{ userFeedback.feedback }}</div>
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
const userFeedback = ref({})

watch(() => props.messageId, async (_) => {
    await initUserFeedback()
}, {immediate: true})

async function initUserFeedback() {
    const {data} = await useAsyncData(
        "userFeedback" + props.messageId,
        async () => await $axios.get("/back/api/broker/user-feedback/?message=" + props.messageId)
    )
    userFeedback.value = data.value.data
    if (userFeedback.value.length > 0) {
        userFeedback.value = userFeedback.value[0]
    } else {
        userFeedback.value = {feedback: "No feedback yet"}
    }
}

</script>

<style lang="scss">
.user-feedback-wrapper {
    display: flex;
    flex-direction: row;
    margin-bottom: 10px;
    .user-feedback {
        font-style: italic;
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
