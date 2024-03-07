<template>
    <slot :name="'write-' + fieldName" v-bind:schema="schema" v-bind:form="form" v-bind:fieldName="fieldName"
          v-bind:formServerErrors="formServerErrors">
        <el-form-item v-if="schema.properties[fieldName]"
                      :label="schema.properties[fieldName].type === 'boolean' || noLabel ? '' : $t(fieldName)"
                      :prop="fieldName"
                      :error="formServerErrors[fieldName]">
            <el-checkbox v-if="schema.properties[fieldName].type === 'boolean'" v-model="form[fieldName]"
                         :label="$t(fieldName)"/>

            <InputSelect v-else-if="isSelect"
                         :schema="schema"
                         :form="form"
                         :fieldName="fieldName"/>
            <FileField v-else-if="schema.properties[fieldName].type === 'file'" :form="form" :fieldName="fieldName"/>
            <el-input v-else v-model="form[fieldName]"/>
        </el-form-item>
    </slot>
</template>
<script setup>
import InputSelect from "~/components/generic/InputSelect.vue";
import FileField from "~/components/generic/fields/FileField.vue";

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
    formServerErrors: {
        type: Object,
    },
    noLabel: {
        type: Boolean,
        default: false,
    },
})

const isSelect = computed(() => {
    return props.schema.properties[props.fieldName].type === 'array' || props.schema.properties[props.fieldName].$ref
})

</script>
<style lang="scss">
.el-form-item {
    label {
        color: $chatfaq-color-primary-500;
        font-size: 14px;
        font-weight: 600;
        line-height: 20px;
        letter-spacing: 0em;
        text-align: left;

    }

    div {
        width: 328px;
    }
}

.el-form-item {
    label::after {
        color: $chatfaq-color-primary-500 !important;
    }
}
</style>

<style lang="scss" scoped>
.edit-title {
    font-size: 18px;
    font-weight: 700;
    line-height: 22px;
    color: $chatfaq-color-neutral-black;
    margin-bottom: 24px;
}
</style>
