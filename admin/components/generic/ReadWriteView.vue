<template>
  <ReadView
      v-if="edit === undefined && !add"
      :apiName="apiName"
      :itemName="itemName"
      :cardProps="cardProps"
      :tableProps="tableProps"
  />
  <WriteView
      v-else
      :apiName="apiName"
      :itemName="itemName"
      :schemaName="schemaName"
      :edit="edit"
      :add="add"
  />
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";

const route = useRoute()

const edit = ref(route.params.id)
const add = ref(route.path.endsWith("/add/"))

watch(route, value => {
  add.value = route.path.endsWith("/add/")
  edit.value = route.params.id
}, {deep: true, immediate: true})

const props = defineProps({
  apiName: {
    type: String,
    mandatory: true
  },
  itemName: {
    type: String,
    mandatory: true
  },
  schemaName: {
    type: String,
    mandatory: true
  },
  cardProps: {
    type: Object,
    mandatory: true
  },
  tableProps: {
    type: Object,
    mandatory: true
  },
})
</script>
