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
        <div v-if="uploadProgress > 0 && uploadProgress < 100" class="progress-bar">
            <div class="progress" :style="{ width: uploadProgress + '%' }"></div>
        </div>
        <div v-if="uploadError" class="error-message">
            {{ uploadError }}
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import { ref } from "vue";

const store = useGlobalStore();
const fileInput = ref(null);
const uploadProgress = ref(0);
const uploadError = ref(null);

const props = defineProps({
    presignedUrl: {
        type: String,
        required: false,
    },
    contentType: {
        type: String,
        required: false,
    },
    uploadPath: {
        type: String,
        required: false,
    },
});

const emit = defineEmits(['fileSelected', 'uploadPath']);

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        if (file.size > 10 * 1024 * 1024) { // 10MB limit
            alert('El archivo no debe superar los 10MB');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        if (props.presignedUrl) {
            uploadFileToS3(file);
        } else {
            emit('fileSelected', file);
        }
    }
}

async function uploadFileToS3(file) {
    try {
        uploadProgress.value = 0;
        uploadError.value = null;

        const response = await fetch(props.presignedUrl, {
            method: 'PUT',
            headers: {
                'Content-Type': props.contentType,
            },
            body: file,
            onUploadProgress: (progressEvent) => { // TODO: fix this
                const progress = Math.round((progressEvent.loaded / progressEvent.total) * 100);
                console.log('progress: ', progress);
                uploadProgress.value = progress;
            },
        });

        if (!response.ok) {
            throw new Error('Error al subir el archivo a S3');
        }
        console.log('File uploaded successfully to: ', props.uploadPath);
        emit('uploadPath', props.uploadPath);
    } catch (error) {
        console.error('Error uploading file:', error);
        uploadError.value = 'Error al subir el archivo. Por favor, inténtalo de nuevo.';
    } finally {
        fileInput.value.value = ''; // Clear the input
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

    .progress-bar {
        height: 8px;
        background-color: #e0e0e0;
        border-radius: 4px;
        margin-top: 8px;
        overflow: hidden;

        .progress {
            height: 100%;
            background-color: #4caf50;
            width: 0%;
            transition: width 0.3s ease-in-out;
        }
    }

    .error-message {
        color: #f44336;
        font-size: 12px;
        margin-top: 4px;
    }
}
</style> 