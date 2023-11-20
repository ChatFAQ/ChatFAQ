<template>
  <ReadView
      v-if="editing === undefined && !adding"
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
      :editing="editing"
      :adding="adding"
  />
</template>

<script setup>
import ReadView from "~/components/generic/ReadView.vue";
import {defineProps} from 'vue';
import WriteView from "~/components/generic/WriteView.vue";
import { storeToRefs } from 'pinia'
import {useItemsStore} from "~/store/items.js";
const itemsStore = useItemsStore()


const {editing, adding} = storeToRefs(itemsStore)

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
