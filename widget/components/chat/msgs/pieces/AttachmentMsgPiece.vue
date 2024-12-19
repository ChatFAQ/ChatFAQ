<template>
    <div class="file-download-wrapper">
        <span>{{ props.data.content }}</span>
        <div class="file-download" :class="{ 'dark-mode': store.darkMode }">
            <div class="file-icon-wrapper" :class="{ 'dark-mode': store.darkMode }">
                <File class="file-icon" :class="{ 'dark-mode': store.darkMode }"/>
            </div>
            <div class="file-info">
                <span class="file-name">{{ props.data.name }}</span>
                <span v-if="props.data.name" class="file-type">{{ getFileTypeFromName(props.data.name) }}</span>
            </div>
            <div class="file-download-icon" v-if="props.data.url" @click="downloadFile">
                <Download class="download-icon" :class="{ 'dark-mode': store.darkMode }"/>
            </div>
        </div>
    </div>
</template>

<script setup>
import { useGlobalStore } from "~/store";
import File from "~/components/icons/File.vue";
import Download from "~/components/icons/Download.vue";

const store = useGlobalStore();

const props = defineProps({
    data: {
        type: Object,
        required: true,
    }
});

function downloadFile() {
    window.open(props.data.url, '_blank');
}

function getFileTypeFromName(url) {
    const extension = url.split('.').pop();
    return extension.toUpperCase();
}


</script>

<style scoped lang="scss">
.file-download-wrapper {
    .file-download {
        background-color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 16px;
        // background: $chatfaq-color-chatMessageReference-background-light;
        padding: 10px 20px 10px 10px;
        border-radius: 10px;
        border: 1px solid rgba(0, 25, 120, 0.10);
        margin-top: 8px;
        margin-bottom: 7px;

        &.dark-mode {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }

        .file-icon-wrapper {
            background-color: $chatfaq-file-box-color-light;
            display: flex;
            width: 40px;
            height: 40px;
            padding: 8px;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 10px;
            border-radius: 4px;

            &.dark-mode {
                background: $chatfaq-file-box-color-dark;
            }
        }

        .file-icon {
            width: 16px;
            height: 16px;
            flex-shrink: 0;
            stroke: $chatfaq-file-icon-color-light;

            &.dark-mode {
                stroke: $chatfaq-file-icon-color-dark;
            }
        }

        .file-info {
            display: flex;
            flex-direction: column;

            .file-name {
                color: $chatfaq-color-neutral-black;
                align-self: stretch;
                font-size: 14px;
                font-style: normal;
                font-weight: 600;
                line-height: 20px; /* 142.857% */

                .dark-mode & {
                    color: $chatfaq-color-neutral-white;
                }
            }

            .file-type {
                color: var(--Grey-Scale-600, #8E959F);
                font-feature-settings: 'liga' off, 'clig' off;

                font-family: "Open Sans";
                font-size: 12px;
                font-style: normal;
                font-weight: 400;
                line-height: 18px;

                .dark-mode & {
                    color: $chatfaq-color-chatMessageReferenceTitle-text-dark;
                }
            }
        }
    }

    .file-download-icon {
        color: $chatfaq-color-primary-500;
        stroke: $chatfaq-color-primary-500;
        width: 16px;
        height: 16px;
        cursor: pointer;
        align-self: start;
        padding-left: 10px;
        padding-top: 2px;
    }
}
</style>
