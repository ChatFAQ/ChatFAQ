<template>
    <div class="write-view-wrapper">
        <div class="navigation-header">
            <div class="back-button" @click="stateToRead">
                <el-icon>
                    <ArrowLeft/>
                </el-icon>
                <span>Back</span>
            </div>
            <el-button v-if="!itemsStore.adding" class="add-button" type="primary" round plain>
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
            <div v-if="form[titleProp]" class="edit-title">{{ form[titleProp] }}</div>
            <div v-for="fieldName in Object.keys(schema.properties)" class="field-wrapper">
                <slot :name="fieldName">
                    <el-form-item v-if="excludeFields.indexOf(fieldName) === -1" class="field" :label="fieldName"
                                  :prop="fieldName"
                                  :error="formServerErrors[fieldName]">
                        <el-select v-if="schema.properties[fieldName].$ref" v-model="form[fieldName]">
                            <el-option
                                v-for="choice in schema.properties[fieldName].choices"
                                :key="choice.value"
                                :label="choice.label"
                                :value="choice.value"
                            />
                        </el-select>
                        <el-input v-else v-model="form[fieldName]"/>
                    </el-form-item>
                </slot>
            </div>
        </el-form>

        <div class="commands">
            <el-button v-if="!itemsStore.adding" type="danger" @click="deleting = true" class="delete-button">
                <span v-if="!deleting">Delete</span>
                <el-icon v-else>
                    <Check @click="deleteItem()"/>
                </el-icon>
            </el-button>
            <div v-else></div>
            <div class="flex-right">
                <el-button @click="stateToRead">
                    Cancel
                </el-button>
                <el-button type="primary" @click="submitForm(formRef)">
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
const deleting = ref(false)

const excludeFields = ref(["id", "created_date", "updated_date"])

const props = defineProps({
    apiUrl: {
        type: String,
        required: false,
    },
    titleProp: {
        type: String,
        required: false,
        default: "name",
    },
})
const {data} = await useAsyncData(
    "schema_" + props.apiUrl,
    async () => await itemsStore.getSchemaDef($axios, props.apiUrl)
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
if (itemsStore.editing) {
    const {data} = await useAsyncData(
        props.apiUrl + "_" + itemsStore.editing,
        async () => await itemsStore.requestOrGetItem($axios, props.apiUrl, itemsStore.editing)
    )
    if (data.value) {
        for (const [fieldName, fieldValue] of Object.entries(data.value)) {
            if (excludeFields.value.indexOf(fieldName) === -1) {
                form.value[fieldName] = fieldValue
            }
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
            if (itemsStore.editing)
                await $axios.put(`${props.apiUrl}${itemsStore.editing}/`, form.value)
            else
                await $axios.post(props.apiUrl, form.value)
        } catch (e) {
            if (e.response && e.response.data) {
                for (const [fieldName, errorMessages] of Object.entries(e.response.data)) {
                    formServerErrors.value[fieldName] = errorMessages.join(", ")
                }
            } else {
                throw e
            }
        }
        stateToRead()
    })
}

function deleteItem(id) {
    itemsStore.deleteItem($axios, props.apiUrl, itemsStore.editing)
    deleting.value = undefined
    stateToRead()
}

function stateToRead() {
    itemsStore.adding = false
    itemsStore.editing = undefined
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

        .edit-title {
            font-size: 18px;
            font-weight: 700;
            line-height: 22px;
            color: $chatfaq-color-neutral-black;
            margin-bottom: 24px;
        }

    }

    .commands {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        margin-top: 24px;

        .delete-button {
            width: 75px;
        }

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
