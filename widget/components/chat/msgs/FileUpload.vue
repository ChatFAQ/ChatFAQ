<template>
    <div class="file-upload-wrapper">
        <label class="upload-button" :class="{ 'dark-mode': store.darkMode }">
            <input 
                type="file" 
                @change="handleFileUpload"
                accept=".pdf,.sgm,.sgml,.xml"
                ref="fileInput"
            >
            <span class="button-text">{{ $t('upload_file') }}</span>
        </label>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import { ref } from "vue";

const store = useGlobalStore();
const fileInput = ref(null);

const emit = defineEmits(['fileSelected']);

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.size > 4 * 1024 * 1024) { // 4MB limit
            alert('El archivo no debe superar los 4MB');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        emit('fileSelected', file);
    }
}
</script>

<style scoped lang="scss">
.file-upload-wrapper {
    margin: 12px 0;
    
    .upload-button {
        display: inline-block;
        background: $chatfaq-color-chatMessageReference-background-light;
        border-radius: 4px;
        padding: 6px 12px;
        cursor: pointer;
        
        &.dark-mode {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
        
        input[type="file"] {
            display: none;
        }
    }

    .file-requirements {
        font-size: 12px;
        color: $chatfaq-color-chatMessageReferenceTitle-text-light;
        margin-top: 4px;
        font-style: italic;
        
        &.dark-mode {
            color: $chatfaq-color-chatMessageReferenceTitle-text-dark;
        }
    }
}
</style> 