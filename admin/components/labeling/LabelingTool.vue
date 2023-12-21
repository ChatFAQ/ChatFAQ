<template>
    {{ conversation }}
</template>

<script setup>
import {useItemsStore} from "~/store/items.js";

const itemsStore = useItemsStore()

const router = useRouter()

const {$axios} = useNuxtApp()

const props = defineProps({
    id: {
        type: String,
        mandatory: true
    },
})

// get conversation async data
const {data} = await useAsyncData(
    "conversation"+props.id,
    async () => await $axios.get("/back/api/broker/conversations/"+props.id+"/")
)
const conversation = ref(data.value.data)
</script>

<style lang="scss" scoped>
</style>

