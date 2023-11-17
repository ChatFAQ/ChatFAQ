<template>
    <div class="write-view-wrapper">
        <div class="navigation-header">
            <div class="back-button" @click="navigateToRead">
                <el-icon class="command-delete">
                    <ArrowLeft/>
                </el-icon>
                <span>Back</span>
            </div>
            <el-button v-if="!add" class="add-button" type="primary" round plain>
                History
            </el-button>
        </div>
        <el-form
            class="form-content"
            ref="formRef"
            :model="form"
            :rules="formRules"
            status-icon
            label-position="top"
            require-asterisk-position="right"
            @keydown.enter.native="submitForm(formRef)"
        >
            <div v-for="fieldName in Object.keys(schema.properties)" class="field-wrapper">
                <el-form-item v-if="excludeFields.indexOf(fieldName) === -1" class="field" :label="fieldName" :prop="fieldName" :error="formServerErrors[fieldName]">
                    <el-input v-model="form[fieldName]"/>
                </el-form-item>
            </div>
        </el-form>

        <div class="commands">
            <el-button v-if="!add" type="danger" plain>
                Delete
            </el-button>
            <div v-else></div>
            <div class="flex-right">
                <el-button plain @click="navigateToRead">
                    Cancel
                </el-button>
                <el-button type="primary" plain @click="submitForm(formRef)">
                    Save changes
                </el-button>
            </div>
        </div>
    </div>
</template>
<script setup>
import {useItemsStore} from "~/store/items.js";

const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const router = useRouter()
const schema = ref({})
const formRef = ref()

const excludeFields = ref(["id", "created_date", "updated_date"])

const props = defineProps({
    edit: {
        type: Number,
        mandatory: false
    },
    add: {
        type: Boolean,
        mandatory: false
    },
    schemaName: {
        type: String,
        mandatory: true
    },
    apiName: {
        type: String,
        required: true,
    },
})

const {data} = await useAsyncData(
    "schema",
    async () => await itemsStore.requestOrGetSchema($axios, props.schemaName)
)
schema.value = data.value

const form = ref({})
const formServerErrors = ref({})
const formRules = ref({})

// Initialize form
for (const [fieldName, fieldInfo] of Object.entries(schema.value.properties)) {
    if (excludeFields.value.indexOf(fieldName) === -1) {
        form.value[fieldName] = undefined
        formServerErrors.value[fieldName] = undefined
        formRules.value[fieldName] = []
        if (schema.value.required.indexOf(fieldName) !== -1) {
            formRules.value[fieldName].push({required: true, message: `Please enter ${fieldName}`, trigger: 'blur'})
        }
    }
}

// Initialize form values
if (props.edit) {
    const { data } = await useAsyncData(
        async () => await itemsStore.requestOrGetItem($axios, props.apiName, props.schemaName, props.edit)
    )
    console.log(data)
    for (const [fieldName, fieldValue] of Object.entries(data.value)) {
        if (excludeFields.value.indexOf(fieldName) === -1) {
            form.value[fieldName] = fieldValue
        }
    }
}

const submitForm = async (formEl) => {
    if (!formEl) return
    await formEl.validate()
    await formEl.validate(async (valid) => {
        if (!valid)
            return
        try {
            if (props.edit)
                await $axios.put(`/back/api/language-model/${props.apiName}/${props.edit}/`, form.value)
            else
                await $axios.post(`/back/api/language-model/${props.apiName}/`, form.value)
        } catch (e) {
            if (e.response && e.response.data) {
                for (const [fieldName, errorMessages] of Object.entries(e.response.data)) {
                    formServerErrors.value[fieldName] = errorMessages.join(", ")
                }
            } else {
                throw e
            }
        }
        router.push({
            path: `/ai_config/${props.apiName}/`,
        });
    })
}
function navigateToRead() {
    router.push({
        path: `/ai_config/${props.apiName}/`,
    });
}
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
.write-view-wrapper {
    display: flex;
    flex-wrap: wrap;
    margin-left: 160px;
    margin-right: 160px;
    max-width: 1300px;
    .navigation-header {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 24px;
        .back-button {
            display: flex;
            cursor: pointer;
            align-items: center;
            font-size: 12px;
            font-weight: 600;
            color: $chatfaq-color-primary-500;
            i {
                margin-right: 8px;
            }
        }
    }
    .form-content {
        background-color: white;
        border-radius: 10px;
        width: 100%;
        margin-top: 16px;
        padding: 28px;
        border: 1px solid $chatfaq-color-primary-200;

    }
    .commands {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        margin-top: 24px;
        .flex-right {
            display: flex;
            flex-direction: row;
            *:first-child {
                margin-right: 8px;
            }
        }
    }

}
</style>
