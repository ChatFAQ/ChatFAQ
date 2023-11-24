<template>
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
    <el-button @click="toggleEditingPassword"></el-button>
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
