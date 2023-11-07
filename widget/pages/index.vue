<template>
    <client-only>
        <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :manageUserId="manageUserId" :title="title"
                :subtitle="subtitle" :historyOpenedDesktop="historyOpenedDesktop"  :historyOpenedMobile="historyOpenedMobile" :fullScreen="fullScreen"/>
    </client-only>
</template>
<script setup>
const conf = useRuntimeConfig()

const chatfaqWS = ref(conf.public.chatfaqWS)
const chatfaqAPI = ref(conf.public.chatfaqAPI)
const manageUserId = ref(true)
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
const fsmDef = ref("model_fsm")
const historyOpenedDesktop = ref(true);
const historyOpenedMobile = ref(true);
const fullScreen = ref(true);

</script>
