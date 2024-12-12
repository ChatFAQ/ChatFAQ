<template>
    <div class="file-download-wrapper">
        <div class="file-download" :class="{ 'dark-mode': store.darkMode }">
            <div class="file-icon-wrapper" :class="{ 'dark-mode': store.darkMode }">
                <File class="file-icon" :class="{ 'dark-mode': store.darkMode }"/>
            </div>
            <div class="file-info">
                <span class="file-name">{{ fileName }}</span>
                <span class="file-type">{{ fileType }}</span>
            </div>
            <div class="file-download-icon" v-if="fileUrl" @click="downloadFile">
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
    fileName: {
        type: String,
        required: true
    },
    fileType: {
        type: String,
        required: true
    },
    fileUrl: {
        type: String,
        required: false
    }
});

function downloadFile() {
    window.open(props.fileUrl, '_blank');
}
</script>

<style scoped lang="scss">
.file-download-wrapper {
    margin-top: 8px;
    margin-left: 1950px;
    width: 240px;


    .file-download {
        background-color: #FFFFFF;
        display: flex;
        align-items: center;
        gap: 16px;
        // background: $chatfaq-color-chatMessageReference-background-light;
        padding: 10px 16px;
        border-radius: 10px;
        border: 1px solid rgba(0, 25, 120, 0.10);

        &.dark-mode {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
        
        .file-icon-wrapper {
            background-color: $chatfaq-color-primary-500;
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
                background: $chatfaq-color-primary-200;
            }
        }

        .file-icon {
            width: 16px;
            height: 16px;
            flex-shrink: 0;
            stroke: #FFF;

            &.dark-mode {
                stroke: $chatfaq-color-primary-500;
            }
        }

        .file-info {
            display: flex;
            flex-direction: column;
            gap: 4px;

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
    }
}
</style>
