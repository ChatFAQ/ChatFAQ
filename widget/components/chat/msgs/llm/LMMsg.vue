<template>
    <div>
        <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
        <span class="reference-index" v-if="isLast" :class="{ 'dark-mode': store.darkMode }"
              v-for="refIndex in data.referenceIndexes">{{ refIndex + 1 }}</span>
    </div>
    <div class="separator-line" :class="{ 'dark-mode': store.darkMode }" v-if="getMarkedDownImages().length"></div>
    <div class="reference-image-wrapper" v-if="getMarkedDownImages().length">
        <div class="reference-image" v-for="(img, index) in getMarkedDownImages()"
             :style="{ 'background-image': 'url(' + imageUrls[img.file_name] + ')' }">
            <div class="reference-image-index target">{{ index + 1 }}</div>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {computed} from "vue";

const store = useGlobalStore();

const props = defineProps(["data", "isLast"]);
const hightlight_light = "#4630751a"
const hightlight_dark = "#1A0438"

function getMarkedDownImages() {
    const images = props.data.payload.model_response.match(/!\[([^\]]+)\][ \n]*\(([^\)]+)\)/g);
    if (images) {
        return images.map((image) => {
            const imageRegex = /!\[([^\]]+)\][ \n]*\(([^\)]+)\)/;
            const imageMatch = image.match(imageRegex);
            return {
                alt: imageMatch[1],
                file_name: imageMatch[2],
            };
        });
    }
    return [];
}

function replaceMarkedDownImagesByReferences() {
    const images = props.data.payload.model_response.match(/!\[([^\]]+)\][ \n]*\(([^\)]+)\)/g);
    let res = props.data.payload.model_response;
    if (images) {
        images.forEach((image, index) => {
            // capture only the alt text of the image markdown:
            const imageAltRegex = /!\[([^\]]+)\][ \n]*\(([^\)]+)\)/;
            const imageAltMatch = image.match(imageAltRegex);
            // Replace the image by the reference:
            res = res.replace(image, `${imageAltMatch[1]}<span class="reference-image-index" class="${store.darkMode ? 'dark-mode' : ''}">${index + 1}</span>`);
        });
    }
    return res;
}

const markedDown = computed(() => {
    let res = props.data.payload.model_response;
    res = replaceMarkedDownImagesByReferences(res)
    const hightlight = store.darkMode ? hightlight_dark : hightlight_light
    // regex for detecting and represent markdown links:
    const linkRegex = /\[([^\]]+)\][ \n]*\(([^\)]+)\)/g;
    res = res.replace(linkRegex, '<a target="_blank" href="$2">$1</a>');
    // regex for detecting and represent markdown lists:
    const listRegex = /(?:^|\n)(?:\*|\-|\d+\.)\s/g;
    res = res.replace(listRegex, '<br/>- ');
    // regex for detecting and represent the character: ` highlighting ex: bla bla `bla` bla:
    const highlightRegex = /`([^`]+)`/g;
    res = res.replace(highlightRegex, '<span style="background-color: ' + hightlight + '; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span>');
    // regex for detecting and representing codeblocks with tab  character:
    const codeBlockRegex = /(?:^|\n)(?:\t)([^\n]+)/g;
    const codeBlockRegex2 = /(?:^|\n)(?:    )([^\n]+)/g;
    res = res.replace(codeBlockRegex, '<span style="background-color: ' + hightlight + '; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span><br/>');
    res = res.replace(codeBlockRegex2, '<span style="background-color: ' + hightlight + '; padding: 0px 3px 0px 3px; border-radius: 2px;">$1</span><br/>');
    // regex for detecting and representing markdown bold text:
    const boldRegex = /\*\*([^\*]+)\*\*/g;
    res = res.replace(boldRegex, '<b>$1</b>');

    return res
});

const imageUrls = computed(() => {
    const res = {}
    if (!props.data.payload.references.knowledge_items)
        return res

    props.data.payload.references.knowledge_items.forEach(item => {
        Object.assign(res, item.image_urls)
    })
    return res
})

</script>
<style lang="scss">

.marked-down-content {
    white-space: pre-wrap;
    display: inline;

    * {
        display: inline;
    }

    p {
        margin: 0;
    }

    a {
        color: $chatfaq-color-chatMessageReference-text-light;
        background: $chatfaq-color-chatMessageReference-background-light;
        border-radius: 4px;
        padding: 0px 6px 0px 6px;
        text-decoration: none;
    }

    &.dark-mode {
        a {
            background: $chatfaq-color-chatMessageReference-background-dark;
            color: $chatfaq-color-chatMessageReference-text-dark;
        }
    }
}

.reference-index {
    margin-right: 2px;
    font-size: 8px;
    padding: 0px 3px 0px 3px;
    border-radius: 2px;
    color: $chatfaq-color-chatMessageReference-text-light;
    background: $chatfaq-color-chatMessageReference-background-light;

    &.dark-mode {
        color: $chatfaq-color-chatMessageReference-text-light;
        background: $chatfaq-color-chatMessageReference-background-light;
    }
}

.reference-image-index {
    position: relative;
    width: fit-content;
    line-height: 12px;
    margin-right: 2px;
    font-size: 8px;
    padding: 0px 3px 0px 3px;
    border-radius: 2px;
    top: -7px;
    left: 0px;
    color: $chatfaq-color-primary-200;
    background: $chatfaq-color-primary-500;

    &.dark-mode {
        color: $chatfaq-color-primary-200;
        background: $chatfaq-color-primary-500;
    }

    &.target {
        position: absolute;
        top: -5px !important;
        left: -5px !important;
    }
}

.reference-image-wrapper {
    display: flex;
    flex-wrap: wrap;

    .reference-image {
        position: relative;
        margin-right: 12px;
        margin-bottom: 8px;
        background-size: 123px;
        width: 123px;
        height: 80px;
        border-radius: 6px;
    }
}

.separator-line {
    height: 1px;
    background-color: $chatfaq-color-separator-light;
    align-content: center;
    text-align: center;
    margin-top: 8px;
    margin-bottom: 8px;

    &.dark-mode {
        background-color: $chatfaq-color-separator-dark;
    }
}
</style>

