<template>
    <client-only>
        <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :manageUserId="manageUserId" :title="title"
                :subtitle="subtitle" :historyOpened="historyOpened"  :historyOpenedMobile="historyOpenedMobile"
                :fullScreen="fullScreen" :displayGeneration="displayGeneration" :displaySources="displaySources" :sourcesFirst="sourcesFirst"
                :preview-mode="false"
        />
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
const historyOpened = ref(true);
const fullScreen = ref(false);
const displayGeneration = ref(true);
const displaySources = ref(true);
const sourcesFirst = ref(false);

</script>
