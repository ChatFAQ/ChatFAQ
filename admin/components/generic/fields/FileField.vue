<template>
    <div class="file-field-wrapper">
        <el-upload drag :auto-upload="false" @change="fileUpload" @remove="fileUpload(undefined)">
            <el-icon>
                <upload/>
            </el-icon>
            <div class="el-upload__text" v-html="$t('droporclickupload')"></div>
        </el-upload>
        <div class="uploaded-file" v-if="form[fieldName]">
            <div>
                <el-icon><Document/></el-icon>
                <a class="doc-name" :href="form[fieldName]" target="_blank">{{form[fieldName].split("/").pop().split("?").shift()}}</a>
            </div>
            <el-icon class="close" @click="form[fieldName] = undefined"><Close/></el-icon>
        </div>
    </div>
</template>

<script setup>

import { ref, defineExpose, defineProps } from 'vue'

const uploadedFile = ref(null)
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
    uploadedFile.value = uploadFile
    props.form[props.fieldName] = undefined
}
function submit() {
    if(!uploadedFile.value && props.form[props.fieldName]) {
        delete props.form[props.fieldName]
    } else if (uploadedFile.value) {
        props.form[props.fieldName] = uploadedFile.value
    }
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
