<template>
    <WidgetLoader :chatfaqWs="runtimeConfig.chatfaqWS" :chatfaqApi="runtimeConfig.chatfaqAPI" :title="title" :subtitle="subtitle"/>
</template>
<script setup>
const runtimeConfig = useRuntimeConfig()
const title = ref("Hello there 👋")
const subtitle = ref("How can we help you?")

</script>
