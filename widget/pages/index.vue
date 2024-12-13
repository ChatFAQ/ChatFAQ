<template>
    <client-only>
        <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :title="title"
                :subtitle="subtitle" allow-attachments speech-recognition speech-recognition-auto-send
        />
    </client-only>
</template>
<script setup>
const conf = useRuntimeConfig()

const chatfaqWS = ref(conf.public.chatfaqWS)
const chatfaqAPI = ref(conf.public.chatfaqAPI)
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
const fsmDef = ref("file_fsm")

</script>
