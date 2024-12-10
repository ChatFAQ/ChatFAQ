<template>
    <div class="file-upload-wrapper">
        <label class="upload-button" :class="{ 'dark-mode': store.darkMode }">
            <input 
                type="file" 
                @change="handleFileUpload"
                ref="fileInput"
                :accept="acceptedFileExtensions"
            >
            <span class="button-text">{{ $t('upload_file') }}</span>
            <FileAttachment class="file-icon" />
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
import { ref, computed } from "vue";

import FileAttachment from "~/components/icons/FileAttachment.vue";

const store = useGlobalStore();
const fileInput = ref(null);
const uploadProgress = ref(0);
const uploadError = ref(null);
const selectedFileExtension = ref(null);

const props = defineProps({
    fileRequest: {
        type: Object,
        required: true,
    },
});

const emit = defineEmits(['fileSelected', 'uploadPath']);

const acceptedFileExtensions = computed(() => {
    return Object.keys(props.fileRequest).map(ext => '.' + ext).join(',');
});

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFileExtension.value = file.name.split('.').pop().toLowerCase();
        if (!props.fileRequest[selectedFileExtension.value]) {
            alert('Tipo de archivo no permitido.');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        const { max_size } = props.fileRequest[selectedFileExtension.value];
        if (file.size > max_size) { 
            alert('El archivo no debe superar los ' + max_size / (1024 * 1024) + ' MB');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        if (props.fileRequest[selectedFileExtension.value].presigned_url) {
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
        const { presigned_url, upload_path, content_type } = props.fileRequest[selectedFileExtension.value];

        const response = await fetch(presigned_url, {
            method: 'PUT',
            headers: {
                'Content-Type': content_type,
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
        console.log('File uploaded successfully');
        emit('uploadPath', upload_path);
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
        display: flex;
        align-items: center;
        gap: 16px;
        background: $chatfaq-color-chatMessageReference-background-light;
        padding: 10px 16px;
        cursor: pointer;
        border-radius: 10px;
        border: 1px solid rgba(0, 25, 120, 0.10);
        // background: #FFF;
        
        .file-icon {
            width: 16px;
            height: 16px;
        }
        
        &.dark-mode {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
        
        input[type="file"] {
            display: none;
        }
    }

    .button-text {
        color: #001978;
        font-feature-settings: 'liga' off, 'clig' off;
        font-size: 14px;
        font-style: normal;
        font-weight: 700;
        line-height: 20px; /* 142.857% */
        text-decoration-line: underline;
        text-decoration-style: solid;
        text-decoration-skip-ink: auto;
        text-decoration-thickness: auto;
        text-underline-offset: auto;
        text-underline-position: from-font;
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