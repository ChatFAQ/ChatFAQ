<template>
  <div>
    <Widget />
  </div>
</template>
<script setup>
import { useGlobalStore } from "~/store";
const store = useGlobalStore()
const runtimeConfig = useRuntimeConfig()

store.chatfaqWS = runtimeConfig.chatfaqWS;
store.chatfaqAPI = runtimeConfig.chatfaqAPI;

</script>
