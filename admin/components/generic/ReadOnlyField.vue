<template>
    <slot :name="'write-' + fieldName" v-bind:value="value" v-bind:fieldName="fieldName">
        <span class="field-name">{{ $t(fieldName) }}:</span>
        <span class="field-value">{{ value }}</span>
    </slot>
</template>
<script setup>
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
    value: {
        type: String,
        required: true,
    },
})
</script>
<style lang="scss">
</style>

<style lang="scss" scoped>
.field-name {
    color: $chatfaq-color-primary-500;
    font-size: 14px;
    font-weight: 600;
    line-height: 20px;
    letter-spacing: 0em;
    text-align: left;
    margin-right: 8px;
}

.field-value {
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    letter-spacing: 0em;
    text-align: left;

}
</style>
