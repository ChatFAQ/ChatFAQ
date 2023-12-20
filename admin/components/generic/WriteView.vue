<template>
    <div class="write-view-wrapper">
        <div class="navigation-header">
            <div class="back-button" @click="itemsStore.stateToRead">
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
            :scroll-to-error="true"
            :scroll-into-view-options="{ behavior: 'smooth', block: 'center' }"
        >
            <div v-if="!Object.keys(sections).length" class="form-section">
                <div class="edit-title">{{ createTitle(form) }}</div>
                <div v-for="(_, fieldName) in filterInSection(true, schema.properties)">
                    <FormField
                        v-if="allExcludeFields.indexOf(fieldName) === -1 && !props.readOnly"
                        :fieldName="fieldName"
                        :schema="schema"
                        :form="form"
                        :formServerErrors="formServerErrors"
                        :ref="el => fieldsRef[fieldName] = el"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="data"></slot>
                        </template>
                    </FormField>
                    <ReadOnlyField v-else-if="allExcludeFields.indexOf(fieldName) === -1 && props.readOnly"
                                   :fieldName="fieldName"
                                   :schema="schema"
                                   :value="form[fieldName]"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="data"></slot>
                        </template>
                    </ReadOnlyField>
                </div>
            </div>
            <div v-else v-for="(fields, sectionName) in filterInSection(true, sections)" class="form-section">
                <div class="edit-title">{{ sectionName }}</div>
                <div v-for="fieldName in fields">
                    <FormField
                        v-if="allExcludeFields.indexOf(fieldName) === -1 && !props.readOnly"
                        :fieldName="fieldName"
                        :schema="schema"
                        :form="form"
                        :formServerErrors="formServerErrors"
                        :ref="el => fieldsRef[fieldName] = el"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="data"></slot>
                        </template>
                    </FormField>
                    <ReadOnlyField v-else-if="allExcludeFields.indexOf(fieldName) === -1 && props.readOnly"
                                   :fieldName="fieldName"
                                   :schema="schema"
                                   :value="form[fieldName]"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="data"></slot>
                        </template>
                    </ReadOnlyField>
                </div>
            </div>
            <div v-for="(_, fieldName) in filterInSection(false, schema.properties)">
                <FormField
                    v-if="allExcludeFields.indexOf(fieldName) === -1 && !props.readOnly"
                    :fieldName="fieldName"
                    :schema="schema"
                    :form="form"
                    :formServerErrors="formServerErrors"
                    :noLabel="true"
                    :ref="el => fieldsRef[fieldName] = el"
                >
                    <template v-for="(_, name) in $slots" v-slot:[name]="data">
                        <slot :name="name" v-bind="data"></slot>
                    </template>
                </FormField>
                <ReadOnlyField v-else-if="allExcludeFields.indexOf(fieldName) === -1 && props.readOnly"
                               :fieldName="fieldName"
                               :schema="schema"
                               :value="form[fieldName]"
                >
                    <template v-for="(_, name) in $slots" v-slot:[name]="data">
                        <slot :name="name" v-bind="data"></slot>
                    </template>
                </ReadOnlyField>
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
                <el-button @click="itemsStore.stateToRead">
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
import {ref} from "vue";
import {useItemsStore} from "~/store/items.js";
import FormField from "~/components/generic/FormField.vue";
import ReadOnlyField from "~/components/generic/ReadOnlyField.vue";

const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const router = useRouter()
const schema = ref({})
const formRef = ref()
const fieldsRef = ref({})
const deleting = ref(false)
const emit = defineEmits(['submitForm'])

const props = defineProps({
    apiUrl: {
        type: String,
        required: false,
    },
    titleProps: {
        type: Array,
        required: false,
        default: ["name"],
    },
    excludeFields: {
        type: Array,
        required: false,
        default: [],
    },
    sections: {
        type: Object,
        required: false,
        default: {},
    },
    outsideSection: {
        type: Array,
        required: false,
        default: [],
    },
    readOnly: {
        type: Boolean,
        required: false,
        default: false,
    },
})
itemsStore.loading = true

const {data} = await useAsyncData(
    "schema_" + props.apiUrl,
    async () => await itemsStore.getSchemaDef($axios, props.apiUrl)
)
itemsStore.loading = false
schema.value = data.value
const form = ref({})
const formServerErrors = ref({})
const formRules = ref({})
const allExcludeFields = computed(() => {
    return [...props.excludeFields, "id", "created_date", "updated_date"]
})

// Initialize form
for (const [fieldName, fieldInfo] of Object.entries(schema.value.properties)) {
    if (allExcludeFields.value.indexOf(fieldName) === -1) {
        form.value[fieldName] = undefined
        formServerErrors.value[fieldName] = undefined
        formRules.value[fieldName] = []
        if (schema.value.required.indexOf(fieldName) !== -1) {
            formRules.value[fieldName].push({required: true, message: `Please enter ${fieldName}`, trigger: 'blur'})
        }
    }
}


// Initialize form values
initializeFormValues()
watch(() => itemsStore.editing, initializeFormValues)
async function initializeFormValues() {
    if (itemsStore.editing) {
        itemsStore.loading = true
        const {data} = await useAsyncData(
            props.apiUrl + "_" + itemsStore.editing,
            async () => await itemsStore.requestOrGetItem($axios, props.apiUrl, itemsStore.editing)
        )
        if (data.value) {
            for (const [fieldName, fieldValue] of Object.entries(data.value)) {
                if (allExcludeFields.value.indexOf(fieldName) === -1) {
                    form.value[fieldName] = fieldValue
                }
            }
        }
        itemsStore.loading = false
    }
}

function createTitle(form) {
    return props.titleProps.map(prop => form[prop]).join(" ")
}

const submitForm = async (formEl) => {

    if (!formEl) return
    await formEl.validate(async (valid) => {
        if (!valid)
            return
        // emit event "submitForm":
        emit("submitForm", form.value)
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
                const ref = fieldsRef.value[Object.keys(e.response.data)[0]]
                ref.$el.parentElement.scrollIntoView({behavior: "smooth", block: "center"})
                return
            } else {
                throw e
            }
        }
        itemsStore.stateToRead()
    })
}

function deleteItem(id) {
    itemsStore.deleteItem($axios, props.apiUrl, itemsStore.editing)
    deleting.value = undefined
    itemsStore.stateToRead()
}

function filterInSection(inSection, _obj) {
    const res = Object.keys(_obj)
        .filter(key => inSection ? !props.outsideSection.includes(key) : props.outsideSection.includes(key))
        .reduce((obj, key) => {
            obj[key] = _obj[key];
            return obj;
        }, {});
    return res
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
    margin-left: 120px;
    margin-right: 120px;
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

    .commands {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100%;
        margin-bottom: 40px;

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
