<template>
    <div class="file-field-wrapper">
        <el-upload drag :auto-upload="false" @change="fileUpload" @remove="fileUpload(undefined)" ref="upload" :limit="1">
            <el-icon>
                <upload/>
            </el-icon>
            <div class="el-upload__text" v-html="$t('droporclickupload')"></div>
        </el-upload>
        <div class="uploaded-file" v-if="existingFile && existingFile.length">
            <div>
                <el-icon><Document/></el-icon>
                <a class="doc-name" :href="existingFile" target="_blank">{{existingFile.split("/").pop().split("?").shift()}}</a>
            </div>
            <el-icon class="close" @click="existingFile = undefined"><Close/></el-icon>
        </div>
    </div>
</template>

<script setup>

import { ref, defineProps, watch } from 'vue'

const upload = ref(null)

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
const existingFile = ref(props.form[props.fieldName] || "")
watch(() => props.form[props.fieldName], (newValue, oldValue) => {
    if (typeof newValue === "string") {
        existingFile.value = newValue
        props.form[props.fieldName] = undefined
    }
})

existingFile.value = props.form[props.fieldName]
function fileUpload(uploadFile) {
    if (!uploadFile) {
        props.form[props.fieldName] = undefined
        return
    }
    props.form[props.fieldName] = uploadFile.raw
    existingFile.value = undefined
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
