<template>
    <client-only>
        <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :userId="userId" :title="title"
                :subtitle="subtitle" :historyOpened="historyOpened"/>
    </client-only>
</template>
<script setup>
const conf = useRuntimeConfig()

const chatfaqWS = ref(conf.public.chatfaqWS)
const chatfaqAPI = ref(conf.public.chatfaqAPI)
const userId = ref(undefined)
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
const fsmDef = ref("model_fsm")
const historyOpened = ref(false);

onMounted(() => {
    historyOpened.value = (screen.width / screen.height) > 1;
})

function uuidv4() {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
        (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
    );
}

if (process.client) {

    userId.value = localStorage.getItem("chatfaq-user-identifier")
    if (!userId.value) {
        localStorage.setItem("chatfaq-user-identifier", uuidv4())
        userId.value = localStorage.getItem("chatfaq-user-identifier")
    }
}
</script>
