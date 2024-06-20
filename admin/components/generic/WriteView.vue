<template>
    <div class="write-view-wrapper">
        <div v-if="backButton" class="navigation-header">
            <BackButton @click="emit('exit')"/>
        </div>
        <el-form
            class="form-content"
            ref="formRef"
            :model="form"
            :rules="formRules"
            status-icon
            label-position="top"
            require-asterisk-position="right"
            @keydown.enter.native="submitForm()"
            :scroll-to-error="true"
            :scroll-into-view-options="{ behavior: 'smooth', block: 'center' }"
        >
            <div v-if="!Object.keys(sections).length" class="form-section">
                <div class="edit-title">{{ createTitle(form) }}</div>
                <div v-for="(fieldInfo, fieldName) in filterInSection(true, itemSchema.properties)">
                    <FormField
                        v-if="allExcludeFields.indexOf(fieldName) === -1 && !props.readOnly && !fieldInfo.readOnly"
                        :fieldName="fieldName"
                        :schema="itemSchema"
                        :form="form"
                        :formServerErrors="formServerErrors"
                        :ref="el => fieldsRef[fieldName] = el"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="{...data, form}"></slot>
                        </template>
                    </FormField>
                    <ReadOnlyField
                        v-else-if="allExcludeFields.indexOf(fieldName) === -1 && (props.readOnly ||  fieldInfo.readOnly)"
                        :fieldName="fieldName"
                        :schema="itemSchema"
                        :value="form[fieldName]"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="{...data, form}"></slot>
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
                        :schema="itemSchema"
                        :form="form"
                        :formServerErrors="formServerErrors"
                        :ref="el => fieldsRef[fieldName] = el"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="{...data, form}"></slot>
                        </template>
                    </FormField>
                    <ReadOnlyField v-else-if="allExcludeFields.indexOf(fieldName) === -1 && props.readOnly"
                                   :fieldName="fieldName"
                                   :schema="itemSchema"
                                   :value="form[fieldName]"
                    >
                        <template v-for="(_, name) in $slots" v-slot:[name]="data">
                            <slot :name="name" v-bind="{...data, form}"></slot>
                        </template>
                    </ReadOnlyField>
                </div>
            </div>
            <div v-for="(_, fieldName) in filterInSection(false, itemSchema.properties)">
                <FormField
                    v-if="allExcludeFields.indexOf(fieldName) === -1 && !props.readOnly"
                    :fieldName="fieldName"
                    :schema="itemSchema"
                    :form="form"
                    :formServerErrors="formServerErrors"
                    :noLabel="true"
                    :ref="el => fieldsRef[fieldName] = el"
                >
                    <template v-for="(_, name) in $slots" v-slot:[name]="data">
                        <slot :name="name" v-bind="{...data, form}"></slot>
                    </template>
                </FormField>
                <ReadOnlyField v-else-if="allExcludeFields.indexOf(fieldName) === -1 && props.readOnly"
                               :fieldName="fieldName"
                               :schema="itemSchema"
                               :value="form[fieldName]"
                >
                    <template v-for="(_, name) in $slots" v-slot:[name]="data">
                        <slot :name="name" v-bind="{...data, form}"></slot>
                    </template>
                </ReadOnlyField>
            </div>
        </el-form>
        <slot name="extra-write-bottom" :id="itemId"></slot>
        <div v-if="commandButtons" class="commands">
            <el-button v-if="itemId !== undefined" type="danger" @click="deleteDialogVisible = true"
                       class="delete-button">
                <span>{{ $t("delete") }}</span>
            </el-button>
            <div v-else></div>
            <div class="flex-right">
                <el-button @click="emit('exit')">
                    Cancel
                </el-button>
                <el-button type="primary" @click="submitForm()">
                    Save changes
                </el-button>
            </div>
        </div>
    </div>
    <el-dialog v-model="deleteDialogVisible" :title="$t('warning')" width="500" center>
        <span>
            {{ $t('deleteitemwarning') }}
        </span>
        <template #footer>
            <div class="dialog-footer">
                <el-button @click="() => {deleteDialogVisible = false}">{{ $t('cancel') }}</el-button>
                <el-button type="primary" @click="deleteItem">
                    {{ $t('confirm') }}
                </el-button>
            </div>
        </template>
    </el-dialog>
</template>
<script setup>
import {ref, defineExpose} from "vue";
import {authHeaders, useItemsStore} from "~/store/items.js";
import FormField from "~/components/generic/FormField.vue";
import ReadOnlyField from "~/components/generic/ReadOnlyField.vue";
import BackButton from "~/components/generic/BackButton.vue";
import {ElNotification} from 'element-plus'
import {useI18n} from "vue-i18n";
import {storeToRefs} from "pinia";

const {t} = useI18n();
const {$axios} = useNuxtApp();
const itemsStore = useItemsStore()
const router = useRouter()
const deleteDialogVisible = ref(false)
const form = ref({})
const formServerErrors = ref({})
const formRules = ref({})
const formRef = ref()
const fieldsRef = ref({})
const {schema} = storeToRefs(itemsStore)
const itemSchema = ref({})

const emit = defineEmits(['submitFormStart', 'submitFormEnd', 'exit', 'initializedFormValues'])
defineExpose({submitForm, form})

const props = defineProps({
    itemId: {
        type: String,
        required: false,
    },
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
    conditionalIncludedFields: { // the values are the only fields that are conditionally included if the keys (fields names) are present in the form
        type: Object,
        required: false,
        default: undefined,
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
    order: {
        type: Array,
        required: false,
        default: undefined,
    },
    backButton: {
        type: Boolean,
        required: false,
        default: true,
    },
    commandButtons: {
        type: Boolean,
        required: false,
        default: true,
    },
    leaveAfterSave: {
        type: Boolean,
        required: false,
        default: true,
    },
    itemIdProp: {
        type: String,
        required: false,
        default: "id",
    },
    contentType: {
        type: String,
        required: false,
        default: "multipart/form-data",
    },
})

const allExcludeFields = computed(() => {
    let excludes = []

    if (props.conditionalIncludedFields) {

        const onlyFieldsIfEmpty = Object.keys(props.conditionalIncludedFields)
        if (onlyFieldsIfEmpty.length) {
            let areOnlyFieldsIfEmptyEmpty = true
            for (const field of onlyFieldsIfEmpty) {
                if (form.value[field] !== undefined && form.value[field] !== "") {
                    areOnlyFieldsIfEmptyEmpty = false
                    break
                }
            }
            if (areOnlyFieldsIfEmptyEmpty) {
                const allFields = Object.keys(form.value)
                excludes = allFields.filter(field => !onlyFieldsIfEmpty.includes(field))
            }
        }

        const allFields = Object.keys(form.value)
        for (const [fieldCondition, includedFields] of Object.entries(props.conditionalIncludedFields)) {
            if (form.value[fieldCondition]) {
                excludes = allFields.filter(field => field !== fieldCondition && !includedFields.includes(field))
                break
            }
        }
    }
    return [...props.excludeFields, ...excludes, "id", "created_date", "updated_date"]
})
async function initData() {
    itemsStore.loading = true
    itemSchema.value = await itemsStore.getSchemaDef(props.apiUrl)
    itemsStore.loading = false
}

await initData()


// Initialize form
for (const [fieldName, fieldInfo] of Object.entries(itemSchema.value.properties)) {
    if (allExcludeFields.value.indexOf(fieldName) === -1) {
        form.value[fieldName] = undefined
        formServerErrors.value[fieldName] = undefined
        formRules.value[fieldName] = []
        if (itemSchema.value.required.indexOf(fieldName) !== -1) {
            formRules.value[fieldName].push({required: true, message: `Please enter ${fieldName}`, trigger: 'blur'})
        }
    }
}


// Initialize form values
initializeFormValues()

async function initializeFormValues() {
    if (props.itemId !== undefined) {
        itemsStore.loading = true
        const data = await itemsStore.retrieveItems(props.apiUrl, {
            [props.itemIdProp]: props.itemId,
            limit: 0,
            offset: 0
        }, true) || {}
        for (const [fieldName, fieldValue] of Object.entries(data)) {
            if (allExcludeFields.value.indexOf(fieldName) === -1) {
                form.value[fieldName] = fieldValue
            }
        }
        itemsStore.loading = false
    }
    emit("initializedFormValues", form.value)
}

function createTitle(form) {
    return props.titleProps.map(prop => form[prop]).join(" ")
}

async function submitForm(extraVals = {}, callback = undefined) {
    if (!formRef.value) return true
    await formRef.value.validate(async (valid) => {
        if (!valid) {
            return
        }
        itemsStore.loading = true
        let _itemId = props.itemId
        emit("submitFormStart", props.itemId, form.value)

        form.value = {...form.value, ...extraVals}

        for (const [fieldName, fieldValue] of Object.entries(form.value)) {
            if (fieldValue && fieldValue.unmodifiedFile) {
                delete form.value[fieldName]
            }
        }

        try {
            const headers = {
                'Content-Type': props.contentType,
                ...authHeaders()
            }

            if (props.itemId !== undefined) {
                await $axios.put(`${props.apiUrl}${props.itemId}/`, form.value,  {headers})
            } else {
                const res = await $axios.post(props.apiUrl, form.value,  {headers})
                _itemId = res.data.id
            }
        } catch (e) {
            ElNotification({
                title: 'Error',
                message: t('errorsavingitem'),
                type: 'error',
                position: 'top-right',
            })
            if (e.response && e.response.data) {
                for (const [fieldName, errorMessages] of Object.entries(e.response.data)) {
                    formServerErrors.value[fieldName] = errorMessages.join(", ")
                    if (fieldName === "non_field_errors") {
                        ElNotification({
                            title: 'Error',
                            message: errorMessages,
                            type: 'error',
                            position: 'top-right',
                        })
                    }
                }
                const ref = fieldsRef.value[Object.keys(e.response.data)[0]]
                ref.$el.parentElement.scrollIntoView({behavior: "smooth", block: "center"})
                itemsStore.loading = false
                if (callback)
                    callback(false)
                return
            } else {
                itemsStore.loading = false
                if (callback)
                    callback(false)
                throw e
            }
        }
        emit("submitFormEnd", _itemId, form.value)
        if (props.leaveAfterSave)
            emit('exit')

        ElNotification({
            title: 'Success',
            message: t('successsavingitem'),
            type: 'success',
            position: 'top-right',
        })
        if (callback)
            callback(true)
        itemsStore.loading = false
    })
}

function deleteItem() {
    try {
        itemsStore.loading = true
        itemsStore.deleteItem(props.apiUrl, props.itemId)
        deleteDialogVisible.value = undefined
        emit('exit')
        itemsStore.loading = false
    } catch (e) {
        itemsStore.loading = false
        ElNotification({
            title: 'Error',
            message: t('errordeletingitem'),
            type: 'error',
            position: 'top-right',
        })
    }
    ElNotification({
        title: 'Success',
        message: t('successdeletingitem'),
        type: 'success',
        position: 'top-right',
    })
}

function filterInSection(inSection, _obj) {
    let res = Object.keys(_obj)
        .filter(key => inSection ? !props.outsideSection.includes(key) : props.outsideSection.includes(key))
        .reduce((obj, key) => {
            obj[key] = _obj[key];
            return obj;
        }, {});
    // reorder fields if order is defined
    if (props.order) {
        const ordered = {}
        for (const key of props.order) {
            if (res[key]) {
                ordered[key] = res[key]
                delete res[key]
            }
        }
        res = {...ordered, ...res}
    }
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

.el-form-item__label {
    color: var(--chatfaq-color-primary-500);
    font-size: 14px;
    font-weight: 600;
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

            > *:first-child {
                margin-right: 8px;
            }
        }
    }

}
</style>
