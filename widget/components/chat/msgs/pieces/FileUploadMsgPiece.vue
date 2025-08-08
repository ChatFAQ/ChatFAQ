<template>
    <div class="file-upload-wrapper">
        <span>{{ props.data.content }}</span>
        <label class="upload-button" :class="{ 'dark-mode': store.darkMode }">
            <input
                type="file"
                @change="handleFileUpload"
                ref="fileInput"
                :accept="acceptedFileExtensions"
                :multiple="(props.data.max_files || 1) > 1"
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
import { createMessage } from "~/utils";

import FileAttachment from "~/components/icons/FileAttachment.vue";

const store = useGlobalStore();
const fileInput = ref(null);
const uploadProgress = ref(0);
const uploadError = ref(null);

const props = defineProps({
    data: {
        type: Object,
        required: true,
    },
});


const emit = defineEmits(['fileSelected', 's3Path']);

const acceptedFileExtensions = computed(() => {
    return Object.keys(props.data.files).map(ext => '.' + ext).join(',');
});

async function handleFileUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        const uploadedFiles = [];
        const nonS3Files = [];
        let hasError = false;
        uploadError.value = null;

        // Check max_files limit
        const maxFiles = props.data.max_files || 1;
        if (files.length > maxFiles) {
            uploadError.value = `You can only upload up to ${maxFiles} file${maxFiles > 1 ? 's' : ''} at a time`;
            hasError = true;
        }

        if (!hasError) {
            // First validate all files
            for (const file of files) {
                const fileName = file.name;
                const fileExtension = file.name.split('.').pop().toLowerCase();

                if (!props.data.files[fileExtension]) {
                    uploadError.value = `File type not allowed: ${fileName}`;
                    hasError = true;
                    break;
                }
                const { max_size } = props.data.files[fileExtension];
                if (file.size > max_size) {
                    uploadError.value = `The file ${fileName} must not exceed ${max_size / (1024 * 1024)} MB`;
                    hasError = true;
                    break;
                }
            }
        }

        if (!hasError) {
            // Process all files
            for (let fileIndex = 0; fileIndex < files.length; fileIndex++) {
                const file = files[fileIndex];
                const fileName = file.name;
                const fileExtension = file.name.split('.').pop().toLowerCase();

                if (props.data.files[fileExtension].presigned_urls) {
                    try {
                        const uploadResult = await uploadFileToS3(file, fileExtension, fileName, fileIndex);
                        if (uploadResult) {
                            uploadedFiles.push(uploadResult);
                        }
                    } catch (error) {
                        console.error('Error uploading file:', error);
                        uploadError.value = `Error uploading ${fileName}. Please try again.`;
                        hasError = true;
                        break;
                    }
                } else {
                    nonS3Files.push(file);
                }
            }

            // Only send message if no errors occurred
            if (!hasError) {
                if (uploadedFiles.length > 0) {
                    handleMultipleFilesUploaded(uploadedFiles);
                }
                if (nonS3Files.length > 0) {
                    // Handle non-S3 files (emit for each)
                    nonS3Files.forEach(file => emit('fileSelected', file));
                }
            }
        }

        fileInput.value.value = ''; // Clear the input after processing all files
    }
}

async function uploadFileToS3(file, fileExtension, fileName, fileIndex) {
    uploadProgress.value = 0;
    uploadError.value = null;
    const { presigned_urls, s3_paths, content_type } = props.data.files[fileExtension];
    
    // Use the presigned URL and S3 path for this specific file index
    const presigned_url = presigned_urls[fileIndex];
    const s3_path = s3_paths[fileIndex];

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
        throw new Error('Error uploading file to S3');
    }
    console.log('File uploaded successfully:', fileName);
    
    return {
        s3_path: s3_path,
        name: fileName
    };
}

function handleMultipleFilesUploaded(uploadedFiles) {
    const m = createMessage("human", [{
            "type": "file_uploaded",
            "payload": {
                "files": uploadedFiles.map(file => ({
                    "s3_path": file.s3_path,
                    "name": file.name,
                }))
            },
        }], "0", "0");
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
            stroke: $chatfaq-message-file-attachment-icon-color-light;
            width: 18px;
            height: 18px;

            &.dark-mode {
                stroke: $chatfaq-message-file-attachment-icon-color-dark;
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
        color: $chatfaq-message-file-attachment-text-color-light;
        font-feature-settings: 'liga' off, 'clig' off;
        font-family: "Open Sans";
        font-size: 12px;
        font-style: normal;
        font-weight: 600;
        line-height: 18px; /* 150% */

        &.dark-mode {
            color: $chatfaq-message-file-attachment-text-color-dark;
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
