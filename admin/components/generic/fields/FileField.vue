<template>
    <el-upload drag :auto-upload="false">
        <el-icon>
            <upload/>
        </el-icon>
        <div class="el-upload__text" v-html="$t('droporclickupload')"></div>
    </el-upload>
    -{{form[fieldName]}}-
</template>

<script setup>

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
function submit() {
    // if(!editingPassword.value) {
    //     delete props.form[props.fieldName]
    // }
}
</script>
<style lang="scss">
</style>

<style lang="scss" scoped>
</style>
