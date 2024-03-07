<template>
    <div class="file-field-wrapper">
        <el-upload drag :auto-upload="false" @change="fileUpload">
            <el-icon>
                <upload/>
            </el-icon>
            <div class="el-upload__text" v-html="$t('droporclickupload')"></div>
        </el-upload>
        <div class="uploaded-file" v-if="form[fieldName]">
            <div>
                <el-icon><Document/></el-icon>
                <a class="doc-name" :href="form[fieldName]" target="_blank">{{form[fieldName].split("/").pop()}}</a>
            </div>
            <el-icon class="close" @click="form[fieldName] = undefined"><Close/></el-icon>
        </div>
    </div>
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
function fileUpload(uploadFile) {
    console.log(uploadFile)
}
function submit() {
    // if(!editingPassword.value) {
    //     delete props.form[props.fieldName]
    // }
}
</script>
<style lang="scss">
</style>

<style lang="scss" scoped>
.file-field-wrapper {
    .uploaded-file {
        display: flex;
        padding: 0px 8px;
        border-radius: 5px;
        color: var(--el-text-color-regular);
        &:hover {
            background-color: #f5f7fa;
        }
        .doc-name {
            margin-left: 6px;
            color: var(--el-text-color-regular);
        }
    }
    .close {
        cursor: pointer;
    }
}
</style>
