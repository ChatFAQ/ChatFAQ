<template>
    <el-form-item :label="$t(fieldName)"
                  :prop="fieldName"
                  class="secret-wrapper">
        <el-input
            v-model="form[fieldName]"
            :type="inputType"
            :placeholder="$t(placeholder)"
            :disabled="!editingSecret && oldEncryptedValue"
            show-password
        />
        <el-button v-if="oldEncryptedValue" type="primary" @click="toggleEditingSecret">
            <el-icon>
                <EditPen v-if="!editingSecret"/>
                <Close v-else/>
            </el-icon>
        </el-button>
    </el-form-item>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const editingSecret = ref(false);

const props = defineProps({
    form: {
        type: Object,
        required: true,
    },
    fieldName: {
        type: String,
        required: true,
    },
    placeholder: {
        type: String,
        default: "Please input value",
    },
    inputType: {
        type: String,
        default: "password"
    }
});

const oldEncryptedValue = ref();

watch(() => props.form, () => {
    oldEncryptedValue.value = props.form[props.fieldName];
}, { deep: true, immediate: true });


function toggleEditingSecret(ev) {
    editingSecret.value = !editingSecret.value;
    if (editingSecret.value) {
        props.form[props.fieldName] = "";
    } else {
        props.form[props.fieldName] = oldEncryptedValue.value;
    }
    ev.preventDefault();
}

const submit = () => {
    if (!editingSecret.value) {
        delete props.form[props.fieldName];
    }
};

defineExpose({
    submit,
});

</script>

<style lang="scss">
.secret-wrapper {
    .el-input {
        width: 328px;
    }
    .el-form-item__content {
        display: flex;
        width: unset !important;
    }
}
</style>

<style lang="scss" scoped>
.secret-wrapper {
    button {
        margin-left: 8px;
        height: 40px;
        width: 40px;
    }
}
.el-form-item__content {
    .el-input {
        flex-grow: 1;
        width: unset !important;
    }
}
</style> 