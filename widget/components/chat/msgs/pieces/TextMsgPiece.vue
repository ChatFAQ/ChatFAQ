<template>
    <div>
        <div class="marked-down-content" :class="{ 'dark-mode': store.darkMode }" v-html="markedDown"></div>
        <!-- <span class="reference-index" v-if="isLast" :class="{ 'dark-mode': store.darkMode }"
              v-for="refIndex in data.referenceIndexes">{{ refIndex + 1 }}</span> -->
    </div>
    <div class="separator-line" :class="{ 'dark-mode': store.darkMode }" v-if="getMarkedDownImages.length"></div>
    <div class="reference-image-wrapper" v-if="getMarkedDownImages.length">
        <div class="reference-image" v-for="(img, index) in getMarkedDownImagesTotal"
             :style="{ 'background-image': 'url(' + imageUrls[img.file_name] + ')' }"
             @click="openInNewTab(imageUrls[img.file_name])"

        >
            <div class="reference-image-index target">{{ index + 1 }}</div>
        </div>
        <div class="reference-image-button-paging" v-if="getMarkedDownImages.length > minImgRefs"
             @click="displayAllImgRef = !displayAllImgRef" :class="{ 'dark-mode': store.darkMode }">
            <span v-if="displayAllImgRef">{{ $t("viewless") }}</span>
            <ArrowUpCircle v-if="displayAllImgRef"/>
            <span v-if="!displayAllImgRef">{{ $t("viewmore") }}</span>
            <ArrowDownCircle v-if="!displayAllImgRef"/>
        </div>
    </div>
</template>

<script setup>
import {useGlobalStore} from "~/store";
import {computed, ref, watch, onMounted} from "vue";
import ArrowUpCircle from "~/components/icons/ArrowUpCircle.vue";
import ArrowDownCircle from "~/components/icons/ArrowDownCircle.vue";
import { markdown } from "markdown";

const SpeechSynthesisUtterance = window.SpeechSynthesisUtterance || window.webkitSpeechSynthesisUtterance;
const speechSynthesis = window.speechSynthesis || window.webkitSpeechSynthesis;
const store = useGlobalStore();

const props = defineProps(["data", "isLast", "isLastChunk"]);
const hightlight_light = "#4630751a"
const hightlight_dark = "#1A0438"

const displayAllImgRef = ref(false);
const speechBuffer = ref(''); // Buffer to accumulate unspoken text
const receivedContent = ref(''); // Track the entire received content

const minImgRefs = computed(() => {
    if (store.isPhone)
        return 2
    if (store.maximized)
        return 4
    return 2
})

function replaceMarkedDownImagesByReferences() {
    const images = props.data.payload.content.match(/!\[([^\]]+)\][ \n]*\(([^\)]+)\)/g);
    let res = props.data.payload.content;
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
    let res = props.data.payload.content;
    res = replaceMarkedDownImagesByReferences(res)
    return markdown.toHTML(res);
});

const getMarkedDownImages = computed(() => {
    return _getMarkedDownImages()
})

function _getMarkedDownImages() {
    const images = props.data.payload.content.match(/!\[([^\]]+)\][ \n]*\(([^\)]+)\)/g);
    if (images) {
        const res = images.map((image) => {
            const imageRegex = /!\[([^\]]+)\][ \n]*\(([^\)]+)\)/;
            const imageMatch = image.match(imageRegex);
            return {
                alt: imageMatch[1],
                file_name: imageMatch[2],
            };
        });
        return res
    }
    return [];
}

const getMarkedDownImagesTotal = computed(() => {
    if (displayAllImgRef.value)
        return _getMarkedDownImages()
    return _getMarkedDownImages().slice(0, minImgRefs.value)

})

const imageUrls = computed(() => {
    return props.data.payload.references.knowledge_item_images || {}
})

function openInNewTab(url) {
    const win = window.open(url, '_blank');
    win.focus();
}

// For non-streaming messages, speak the entire message on initial mount
onMounted(() => {
    if (store.speechSynthesisEnabled && store.speechSynthesisSupported) {
        const content = props.data.payload.content;
        if (content && props.isLastChunk) {
            const utterance = new SpeechSynthesisUtterance(content);
            configureUtterance(utterance);
            speechSynthesis.speak(utterance);
        }
    }
});

// Watch for streaming messages
watch(() => ({ data: props.data, isLastChunk: props.isLastChunk }), ({ data: newMessage, isLastChunk }) => {
    if (store.speechSynthesisEnabled && store.speechSynthesisSupported) {
        const newContent = newMessage.payload.content;
        
        // Calculate delta from the last received content
        const delta = newContent.slice(receivedContent.value.length);
        receivedContent.value = newContent; // Update the received content
        
        speechBuffer.value += delta; // Append delta to the buffer

        // Split buffer into complete sentences and remaining text
        const { sentences, remaining } = splitIntoSentences(speechBuffer.value);

        // Speak each complete sentence
        if (sentences.length > 0) {
            sentences.forEach(sentence => {
                const utterance = new SpeechSynthesisUtterance(sentence);
                configureUtterance(utterance);
                speechSynthesis.speak(utterance);
            });
            speechBuffer.value = remaining; // Keep remaining text in buffer
        }
        
        // Speak remaining text when it's the last message
        if (isLastChunk && speechBuffer.value.trim().length > 0) {
            const utterance = new SpeechSynthesisUtterance(speechBuffer.value);
            configureUtterance(utterance);
            speechSynthesis.speak(utterance);
            speechBuffer.value = ''; // Clear buffer after speaking
        }
    }
}, { immediate: false });

function splitIntoSentences(text) {
    // Regex that handles abbreviations and sentence endings
    const sentenceRegex = /\b(\w\.\w\.|[A-Z][a-z]{1,2}\.)|([.?!])\s+(?=[A-Za-z])/g;
    
    // Replace sentence endings with a marker, preserving abbreviations
    const markedText = text.replace(sentenceRegex, (match, g1, g2) => {
        return g1 ? g1 : g2 + "\n";
    });
    
    // Split into sentences and filter out empty strings
    const sentences = markedText.split("\n")
        .map(s => s.trim())
        .filter(s => s.length > 0);
    
    // The remaining text is the last element if it doesn't end with a sentence marker
    const remaining = sentences.pop() || '';
    
    return { sentences, remaining };
}

function configureUtterance(utterance) {
    if (isFinite(store.speechSynthesisPitch)) {
        utterance.pitch = store.speechSynthesisPitch;
    }
    if (isFinite(store.speechSynthesisRate)) {
        utterance.rate = store.speechSynthesisRate;
    }
    if (store.speechSynthesisVoice) {
        const voices = speechSynthesis.getVoices();
        const selectedVoice = voices.find(voice => voice.voiceURI === store.speechSynthesisVoice);
        if (selectedVoice) {
            utterance.voice = selectedVoice;
        }
    }
}

</script>
<style lang="scss">

.marked-down-content {
    // white-space: pre-wrap;
    display: inline;


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

    ol {
        padding-left: 1.5em;
    }

    ul {
        padding-left: 1.5em;
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
        background: $chatfaq-color-chatMessageReference-background-dark;
        color: $chatfaq-color-chatMessageReference-text-dark;
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
        cursor: pointer;
        position: relative;
        margin-right: 6px;
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

.reference-image-button-paging {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 22px;
    padding: 2px 6px 2px 6px;
    border-radius: 4px;
    background: $chatfaq-color-chatMessageReference-background-light;
    color: $chatfaq-color-chatMessageReference-text-light;
    cursor: pointer;
    &.dark-mode {
        background: $chatfaq-color-chatMessageReference-background-dark;
        color: $chatfaq-color-chatMessageReference-text-dark;
    }
    > span {
        margin-right: 4px;
    }
}

.marked-down-content {
    -webkit-font-smoothing: antialiased;
}

</style>

