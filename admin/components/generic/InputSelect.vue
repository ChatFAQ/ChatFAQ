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
            :placeholder="placeholder"
            @change="$emit('change', form)"
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
const filterChoices = ref({})
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
    filterSchema: {
        type: Object,
        required: false,
        default: undefined,
    },
    form: {
        type: Object,
    },
    placeholder: {
        type: String,
        required: false,
        default: "",
    },
})

const isMulti = computed(() => {
    if (props.filterSchema) {
        return props.filterSchema.isMulti
    }
    return props.schema.properties[props.fieldName].type === 'array'
})

const isEnum = computed(() => {
    if (props.filterSchema) {
        return props.filterSchema.type === "enum"
    }
    return props.schema.properties[props.fieldName].choices !== undefined
})

const isRef = computed(() => {
    if (props.filterSchema) {
        return props.filterSchema.type === "ref"
    }
    return props.schema.properties[props.fieldName].choices.results !== undefined
})
onMounted(async () => {
    if (props.filterSchema) {
        if (props.filterSchema.type === "ref") {
            const items = await itemsStore.retrieveItems($axios, props.filterSchema.endpoint)
            items.results = items.results.map((item) => {
                return {
                    value: item.id,
                    label: item.name,
                }
            })
            filterChoices.value.results = items.results
            filterChoices.value.next = items.next
        }
    }
})
const choices = computed(() => {
    if (props.filterSchema && props.filterSchema.type === "enum") {
        return props.filterSchema.choices
    }
    else if (props.filterSchema && props.filterSchema.type === "ref") {
        return filterChoices.value.results || []
    }
    return props.schema.properties[props.fieldName].choices.results ? props.schema.properties[props.fieldName].choices.results : props.schema.properties[props.fieldName].choices
})


function remoteSearch(query) {
    loading.value = true

    setTimeout(() => {
        loading.value = false
    }, 1000)
}

useIntersectionObserver(lastElement, async ([{ isIntersecting }], observerElement) => {
      if (isIntersecting) {
          let resultHolder
          if (props.filterSchema) {
              resultHolder = filterChoices.value
          } else {
              resultHolder = props.schema.properties[props.fieldName].choices
          }
          const next = resultHolder.next
          if (!next)
              return
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
          resultHolder.results.push(...items.results)
          resultHolder.next = items.next
      }
  },
)

</script>
<style lang="scss">
</style>

<style lang="scss" scoped>
</style>
