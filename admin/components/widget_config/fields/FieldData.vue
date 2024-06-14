<template>
    <div class="field-data-wrapper">
        <div v-for="(fields, sectionName) in valuesBySection" class="form-section">
            <div class="light-dark-switch">
                <el-switch
                    v-model="lightDark[sectionName]"
                    v-if="fields[Object.keys(fields)[0]].type === 'color'"
                    size="large"
                    :inactive-text="lightDark[sectionName] ? 'dark' : 'light'"
                />
            </div>
            <div class="edit-title">{{ $t(sectionName) }}</div>
            <div v-for="(field, key) in fields" class="field-wrapper">
                <el-form-item :label="$t(key)" :prop="key">
                    <ColorField v-if="field.type === 'color'" :field="field" :ref="el => subFields[key] = el" :dark="lightDark[sectionName]"/>
                    <GradientField v-else-if="field.type === 'gradient'" :field="field"
                                   :ref="el => subFields[key] = el"/>
                    <FontField v-else-if="field.type === 'font'" :field="field"
                               :ref="el => subFields[key] = el"/>
                    <el-input v-else v-model="field.value" :ref="el => subFields[key] = el"/>
                </el-form-item>

            </div>
        </div>
    </div>
</template>

<script setup>
import ColorField from "~/components/widget_config/fields/ColorField.vue";
import GradientField from "~/components/widget_config/fields/GradientField.vue";
import FontField from "~/components/widget_config/fields/FontField.vue";
import {authHeaders} from "~/store/items.js";

defineExpose({
    submit,
})
const {$axios} = useNuxtApp();
const subFields = ref({})

const props = defineProps({
    form: {
        type: Object,
        mandatory: true
    },
    fieldName: {
        type: String,
        mandatory: true
    }
})

const {data} = await useAsyncData(
    "theme-defaults",
    async () => await $axios.get('/back/api/widget/theme-defaults/', {headers: authHeaders()})
)
const defaults = ref(data.value.data)

const valuesBySection = computed(() => {
    const _valuesBySection = {}
    for (const [key, value] of Object.entries(defaults.value)) {
        if (_valuesBySection[value.section] === undefined) {
            _valuesBySection[value.section] = {}
        }
        _valuesBySection[value.section][key] = value
        if (props.form[props.fieldName] && props.form[props.fieldName][key] !== undefined) {
            _valuesBySection[value.section][key] = props.form[props.fieldName][key]
        }
    }
    return _valuesBySection
})
const lightDark = ref({})
for (let sectionName in valuesBySection.value) {
    lightDark.value[sectionName] = false
}

function submit() {
    const res = {}
    for (const [key, subField] of Object.entries(subFields.value)) {
        if (subField.getValue) {
            res[key] = subField.getValue()
        } else if (subField.input) {
            res[key] = subField.input.value
        }
    }
    props.form[props.fieldName] = res
}
</script>

<style lang="scss" scoped>
.field-data-wrapper {
    width: 100%;

    .form-section {
        background-color: white;
        border-radius: 10px;
        width: 100%;
        margin-top: 16px;
        margin-bottom: 24px;
        padding: 28px;
        border: 1px solid $chatfaq-color-primary-200;
    }

    .edit-title {
        font-size: 18px;
        font-weight: 700;
        line-height: 22px;
        color: $chatfaq-color-neutral-black;
        margin-bottom: 24px;
    }
    .light-dark-switch {
        float: right;
    }
}

</style>
