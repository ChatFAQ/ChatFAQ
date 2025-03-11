<template>
    <client-only>
        <Widget :chatfaqWs="chatfaqWS" :chatfaqApi="chatfaqAPI" :fsmDef="fsmDef" :title="title"
                :subtitle="subtitle" enable-logout :allow-attachments="true" 
                :hideSources="hideSources" :stateOverride="stateOverride" :widgetConfigId="widgetId"
        />
    </client-only>
</template>
<script setup>
import { onMounted } from 'vue';

const conf = useRuntimeConfig()

const chatfaqWS = ref(conf.public.chatfaqWS)
const chatfaqAPI = ref(conf.public.chatfaqAPI)
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")
const fsmDef = ref("llm_fsm")
const hideSources = ref(false)
const stateOverride = ref(null)
const widgetId = ref("6a5fb833-cdcf-468a-ac22-8f1c2b7b1672")

onMounted(() => {
    const urlParams = new URLSearchParams(window.location.search);
    stateOverride.value = urlParams.get('state_override');
})
</script>
