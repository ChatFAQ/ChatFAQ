<template>
    <div class="file-upload-wrapper">
        <span>{{ props.data.content }}</span>
        <label class="upload-button" :class="{ 'dark-mode': store.darkMode }">
            <input
                type="file"
                @change="handleFileUpload"
                ref="fileInput"
                :accept="acceptedFileExtensions"
            >
            <span class="button-text" :class="{ 'dark-mode': store.darkMode }">{{ $t('upload_file') }}</span>
            <FileAttachment class="file-icon" :class="{ 'dark-mode': store.darkMode }" />
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
const selectedFileName = ref(null);

const props = defineProps({
    data: {
        type: Object,
        required: true,
    },
});

console.log('FileUpload', props);

const emit = defineEmits(['fileSelected', 's3Path']);

const acceptedFileExtensions = computed(() => {
    return Object.keys(props.data.files).map(ext => '.' + ext).join(',');
});

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        selectedFileName.value = file.name;
        selectedFileExtension.value = file.name.split('.').pop().toLowerCase();
        if (!props.data.files[selectedFileExtension.value]) {
            alert('Tipo de archivo no permitido.');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        const { max_size } = props.data.files[selectedFileExtension.value];
        if (file.size > max_size) {
            alert('El archivo no debe superar los ' + max_size / (1024 * 1024) + ' MB');
            fileInput.value.value = ''; // Clear the input
            return;
        }
        if (props.data.files[selectedFileExtension.value].presigned_url) {
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
        const { presigned_url, s3_path, content_type } = props.data.files[selectedFileExtension.value];

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
        handleFileUploaded(s3_path, selectedFileName.value);
    } catch (error) {
        console.error('Error uploading file:', error);
        uploadError.value = 'Error al subir el archivo. Por favor, inténtalo de nuevo.';
    } finally {
        fileInput.value.value = ''; // Clear the input
    }
}

function handleFileUploaded(s3_path, file_name) {
    const m = {
        "sender": {
            "type": "human",
            "platform": "WS",
        },
        "stack": [{
            "type": "file_uploaded",
            "payload": {
                "s3_path": s3_path,
                "name": file_name,
                // We don't pass url because we don't have it yet
            },
        }],
        "stack_id": "0",
        "stack_group_id": "0",
        "last": true,
    };
    if (store.userId !== undefined)
        m["sender"]["id"] = store.userId

    store.messagesToBeSent.push(m);
    store.messagesToBeSentSignal += 1

}

</script>

<style scoped lang="scss">
.file-upload-wrapper {
    display: flex;
    flex-direction: column;

    .upload-button {
        display: flex;
        align-self: start;
        align-items: center;
        gap: 8px;
        background: $chatfaq-color-chatMessageReference-background-light;
        padding: 8px 10px;
        cursor: pointer;
        border-radius: 4px;
        border: 1px solid rgba(0, 25, 120, 0.10);
        margin-top: 8px;
        margin-bottom: 7px;
        // background: #FFF;

        .file-icon {
            stroke: $chatfaq-color-primary-500;
            width: 18px;
            height: 18px;

            &.dark-mode {
                stroke: $chatfaq-color-chatMessageReference-text-dark;
            }
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
        color: $chatfaq-color-primary-500;
        font-feature-settings: 'liga' off, 'clig' off;
        font-family: "Open Sans";
        font-size: 12px;
        font-style: normal;
        font-weight: 600;
        line-height: 18px; /* 150% */

        &.dark-mode {
            color: $chatfaq-color-chatMessageReference-text-dark;
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
