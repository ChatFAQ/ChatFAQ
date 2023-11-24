<template>
    <div class="password-wrapper">
        <el-input
            v-if="!editingPassword"
            v-model="form[fieldName]"
            type="password"
            placeholder="Please input password"
            disabled
            show-password
        />
        <el-input
            v-else
            v-model="form[fieldName]"
            type="password"
            placeholder="Please input password"
            show-password
        />
        <el-button type="primary" @click=toggleEditingPassword>
            <el-icon>
                <EditPen v-if="!editingPassword"/>
                <Close v-else/>
            </el-icon>
        </el-button>
    </div>
</template>

<script setup>
let oldEncryptedPass

const editingPassword = ref(false)
defineExpose({
    submit,
})
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

function toggleEditingPassword(ev) {
    editingPassword.value = !editingPassword.value
    if(editingPassword.value) {
        oldEncryptedPass = props.form[props.fieldName]
        props.form[props.fieldName] = ""
    } else {
        props.form[props.fieldName] = oldEncryptedPass
    }
    ev.preventDefault()
}

function submit() {
    if(!editingPassword.value) {
        delete props.form[props.fieldName]
    }
}
</script>

<style lang="scss" scoped>
.password-wrapper {
    display: flex;
    flex-direction: row;
    align-items: center;
    button {
        margin-left: 8px;
        height: 40px;
        width: 40px;
    }
}
</style>
