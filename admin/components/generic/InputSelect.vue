<template>
    <client-only>
        <el-select-v2
            v-model="form[fieldName]"
            :multiple="isMulti"
            clearable
            filterable
            :remote="isRef"
            :remote-method="remoteSearch"
            :loading="loading"
            :options="choices"
        >
            <template v-slot:default="props">
                <div v-if="props.index < choices.length - 1">
                    {{ props.item.label }}
                </div>
                <div v-else ref="lastElement">
                    {{ props.item.label }}
                </div>
            </template>
        </el-select-v2>
    </client-only>
</template>
<script setup>
const loading = ref(false)
const lastElement = ref(undefined)
import { useIntersectionObserver } from '@vueuse/core'
import { useItemsStore } from "~/store/items.js";
const { $axios } = useNuxtApp();

const itemsStore = useItemsStore()

const props = defineProps({
    fieldName: {
        type: String,
        required: false,
    },
    schema: {
        type: Object,
        required: false,
        default: {},
    },
    form: {
        type: Object,
    },
})

const isMulti = computed(() => {
    return props.schema.properties[props.fieldName].type === 'array'
})

const isEnum = computed(() => {
    return props.schema.properties[props.fieldName].choices !== undefined
})

const isRef = computed(() => {
    return props.schema.properties[props.fieldName].choices.results !== undefined
})

const choices = computed(() => {
    return props.schema.properties[props.fieldName].choices.results ? props.schema.properties[props.fieldName].choices.results : props.schema.properties[props.fieldName].choices
})


function remoteSearch(query) {
    loading.value = true
    console.log(query)
    setTimeout(() => {
        loading.value = false
    }, 1000)
}

useIntersectionObserver(lastElement, async ([{ isIntersecting }], observerElement) => {
      if (isIntersecting) {
          const next = props.schema.properties[props.fieldName].choices.next
          let url = next.split('?')[0]
          let params = next.split('?')[1]
          params = Object.fromEntries(new URLSearchParams(params))
          const items = await itemsStore.retrieveItems($axios, url, params)
          items.results = items.results.map((item) => {
              return {
                  value: item.id,
                  label: item.name,
              }
          })
          props.schema.properties[props.fieldName].choices.results.push(...items.results)
          props.schema.properties[props.fieldName].choices.next = items.next
      }
  },
)

</script>
<style lang="scss">
</style>

<style lang="scss" scoped>
</style>
