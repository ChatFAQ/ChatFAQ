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
const editingPassword = ref(false)

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
    ev.preventDefault()
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
