<template>
    <div class="field-data-wrapper">
        <div v-for="(fields, sectionName) in defaultsBySection" class="form-section">
            <div class="edit-title">{{ sectionName }}</div>
            <div v-for="(field, key) in fields" class="field-wrapper">
                <el-form-item :label="field.name" :prop="key">
                    <ColorField v-if="field.type === 'color'" :field="field"/>
                    <el-input v-else v-model="field.value"/>
                </el-form-item>

            </div>
        </div>
    </div>
</template>

<script setup>
import ColorField from "~/components/widget_config/fields/ColorField.vue";

const {$axios} = useNuxtApp();

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
    async () => await $axios.get('/back/api/widget/theme-defaults/')
)
const defaults = ref(data.value.data)

const defaultsBySection = computed(() => {
    const defaultsBySection = {}
    for (const [key, value] of Object.entries(defaults.value)) {
        if (defaultsBySection[value.section] === undefined) {
            defaultsBySection[value.section] = {}
        }
        defaultsBySection[value.section][key] = value
    }
    return defaultsBySection
})

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
}

</style>
