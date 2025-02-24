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
import {computed, ref, watch, onMounted, onBeforeUnmount, nextTick} from "vue";
import ArrowUpCircle from "~/components/icons/ArrowUpCircle.vue";
import ArrowDownCircle from "~/components/icons/ArrowDownCircle.vue";
import MarkdownIt from "markdown-it";
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css'; // You can choose a different style

// Create custom renderer for code blocks with top bar and copy button
const md = new MarkdownIt({
    highlight: function (str, lang) {
        // SVG for copy icon
        const copyIconSvg = `<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" style="margin-right: 4px;">
            <g opacity="0.4">
            <path d="M8.66667 14L2.66667 14C2.29848 14 2 13.7015 2 13.3333L2 4.66667C2 4.29848 2.29848 4 2.66667 4L6.39053 4C6.56734 4 6.73691 4.07024 6.86193 4.19526L9.13807 6.4714C9.2631 6.59643 9.33334 6.766 9.33334 6.94281V13.3333C9.33334 13.7015 9.03486 14 8.66667 14Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M6.66602 4L6.66602 2.66667C6.66602 2.29848 6.96449 2 7.33268 2L11.0565 2C11.2334 2 11.4029 2.07024 11.5279 2.19526L13.8041 4.4714C13.9291 4.59643 13.9994 4.766 13.9994 4.94281V11.3333C13.9994 11.7015 13.7009 12 13.3327 12L9.33268 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.33333 7.33333L6.66667 7.33333C6.29848 7.33333 6 7.03486 6 6.66667L6 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M13.9993 5.33333L11.3327 5.33333C10.9645 5.33333 10.666 5.03486 10.666 4.66667L10.666 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </g>
        </svg>`;

        if (lang && hljs.getLanguage(lang)) {
            try {
                const highlighted = hljs.highlight(str, { language: lang }).value;
                // Create a container with top bar and copy button
                return `<div class="code-block-container">
                    <div class="code-block-header${store.darkMode ? ' dark-mode' : ''}">
                        <span class="code-language">${lang}</span>
                        <button class="copy-code-button" data-code="${encodeURIComponent(str)}">
                            ${copyIconSvg}<span>Copy</span>
                        </button>
                    </div>
                    <pre class="hljs language-${lang}${store.darkMode ? ' hljs-dark' : ' hljs-light'}"><code>${highlighted}</code></pre>
                </div>`;
            } catch (__) {}
        }
        
        // If language is not specified or not found, render without language indication
        return `<div class="code-block-container">
            <div class="code-block-header${store.darkMode ? ' dark-mode' : ''}">
                <span class="code-language">code</span>
                <button class="copy-code-button" data-code="${encodeURIComponent(str)}">
                    ${copyIconSvg}<span>Copy</span>
                </button>
            </div>
            <pre class="hljs${store.darkMode ? ' hljs-dark' : ' hljs-light'}"><code>${md.utils.escapeHtml(str)}</code></pre>
        </div>`;
    }
});

const SpeechSynthesisUtterance = window.SpeechSynthesisUtterance || window.webkitSpeechSynthesisUtterance;
const speechSynthesis = window.speechSynthesis || window.webkitSpeechSynthesis;

const store = useGlobalStore();

const props = defineProps(["data", "isLast", "isLastChunk"]);

const displayAllImgRef = ref(false);

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
    res = md.render(res);
    return res;
});

// Function to handle code copying
function copyCode(event) {
    // Find the button element (might be the SVG or span that was clicked)
    let button = event.target;
    while (button && !button.classList.contains('copy-code-button')) {
        button = button.parentElement;
    }
    
    if (!button) return;
    
    const code = decodeURIComponent(button.getAttribute('data-code'));
    
    navigator.clipboard.writeText(code).then(() => {
        // Find the text span inside the button
        const textSpan = button.querySelector('span');
        if (!textSpan) return;
        
        // Save original text and update
        const originalText = textSpan.textContent;
        textSpan.textContent = 'Copied!';
        
        setTimeout(() => {
            textSpan.textContent = originalText;
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy code: ', err);
    });
}

// Function to attach event listeners to copy buttons
function attachCopyListeners() {
    nextTick(() => {
        const copyButtons = document.querySelectorAll('.copy-code-button');
        copyButtons.forEach(button => {
            button.addEventListener('click', copyCode);
        });
    });
}

// Attach event listeners whenever the content changes
watch(() => markedDown.value, attachCopyListeners);

// Update dark mode classes when dark mode changes
watch(() => store.darkMode, (isDark) => {
    nextTick(() => {
        const headers = document.querySelectorAll('.code-block-header');
        headers.forEach(header => {
            if (isDark) {
                header.classList.add('dark-mode');
            } else {
                header.classList.remove('dark-mode');
            }
        });
        
        // Also update code block classes for proper theme application
        const codeBlocks = document.querySelectorAll('pre.hljs');
        codeBlocks.forEach(block => {
            if (isDark) {
                block.classList.add('hljs-dark');
                block.classList.remove('hljs-light');
            } else {
                block.classList.add('hljs-light');
                block.classList.remove('hljs-dark');
            }
        });
    });
});

// Attach listeners on initial mount
onMounted(() => {
    attachCopyListeners();
});

// Clean up listeners before unmount
onBeforeUnmount(() => {
    const copyButtons = document.querySelectorAll('.copy-code-button');
    copyButtons.forEach(button => {
        button.removeEventListener('click', copyCode);
    });
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
    return props.data.payload.references?.knowledge_item_images || {};
})

function openInNewTab(url) {
    const win = window.open(url, '_blank');
    win.focus();
}


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

// ---------------------------------------- Speech logic ----------------------------------------

const speechBuffer = ref(''); // Buffer to accumulate unspoken text
const receivedContent = ref(''); // Track the entire received content

// ------- non-streaming messages -------
onMounted(() => {
    speechIt({ data: props.data, isLastChunk: props.isLastChunk })
});
// ------- streaming messages -------
watch(() => ({ data: props.data, isLastChunk: props.isLastChunk }), speechIt, { immediate: false });

watch (() => store.speechVoicesInitialized, (val) => {
    if (val)
        speechIt({ data: props.data, isLastChunk: props.isLastChunk })
})
watch(() => store.speechRecognitionTranscribing, (val) => {
    if (val)
        cancelSynthesis();
})

function speechIt ({ data: newMessage, isLastChunk }) {
    if (store.speechSynthesisEnabled && store.speechVoicesInitialized) {
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
}

function configureUtterance(utterance) {
    if (isFinite(store.speechSynthesisPitch)) {
        utterance.pitch = store.speechSynthesisPitch;
    }
    if (isFinite(store.speechSynthesisRate)) {
        utterance.rate = store.speechSynthesisRate;
    }
    if (store.speechSynthesisVoices) {
        const voices = speechSynthesis.getVoices();
        const voiceURIs = store.speechSynthesisVoices.split(',');
        const voice = voices.find(voice => voiceURIs.includes(voice.voiceURI));
        if (voice) {
            utterance.voice = voice;
        }
    }
}


function cancelSynthesis() {
    if (speechSynthesis) {
        speechSynthesis.cancel(); // Stop any ongoing speech
        speechBuffer.value = ''; // Clear the speech buffer
        receivedContent.value = ''; // Reset received content
    }
}

onBeforeUnmount(cancelSynthesis);


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

/* Code Block styles */
.code-block-container {
    margin: 8px 0;
    border-radius: 6px;
    overflow: hidden;
    border: 1px solid rgba(0, 0, 0, 0.1);
    background-color: #f8f8f8;
    display: flex;
    flex-direction: column;
    
    pre {
        margin: 0;
        padding: 8px 12px;
        overflow-x: auto;
        flex-grow: 1;
        background-color: inherit;
    }
    
    code {
        font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
        font-size: 0.9em;
        line-height: 1.4;
        display: block;
        white-space: pre;
    }
}

.code-block-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 4px 12px;
    background-color: #e8e8e8;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    font-family: sans-serif;
    font-size: 0.8em;
    min-height: 28px;
    flex-shrink: 0;
    
    &.dark-mode {
        background-color: #2d2d2d;
        color: #e0e0e0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
}

.code-language {
    font-weight: bold;
    font-size: 0.85em;
    color: #666;
    
    .dark-mode & {
        color: #b0b0b0;
    }
}

.copy-code-button {
    background-color: transparent;
    border: 1px solid rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 0.85em;
    font-family: sans-serif;
    cursor: pointer;
    transition: all 0.2s ease;
    outline: none;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    
    svg {
        color: currentColor;
    }
    
    span {
        display: inline-block;
        line-height: 1;
    }
    
    &:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
    
    &:active {
        transform: translateY(1px);
    }
    
    .dark-mode & {
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #e0e0e0;
        
        svg g {
            opacity: 0.7;
        }
        
        &:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
    }
}

/* Update existing hljs styles for dark mode */
.dark-mode {
    .hljs {
        background-color: #1e1e1e;
        color: #dcdcdc;
    }
    
    .code-block-container {
        border: 1px solid rgba(255, 255, 255, 0.1);
        background-color: #1e1e1e;
        
        pre {
            background-color: inherit;
        }
    }
}

/* Style overrides to apply different highlight.js themes */
.hljs-light {
    /* Use github theme (already imported) */
}

.hljs-dark {
    /* Use github-dark theme (already imported) */
}

/* Ensure proper token contrast in dark mode */
.hljs-dark .hljs-keyword,
.hljs-dark .hljs-selector-tag,
.hljs-dark .hljs-title,
.hljs-dark .hljs-section,
.hljs-dark .hljs-doctag,
.hljs-dark .hljs-name,
.hljs-dark .hljs-strong {
    color: #ff79c6;
}

.hljs-dark .hljs-string,
.hljs-dark .hljs-title,
.hljs-dark .hljs-section,
.hljs-dark .hljs-built_in,
.hljs-dark .hljs-literal,
.hljs-dark .hljs-type,
.hljs-dark .hljs-addition,
.hljs-dark .hljs-tag,
.hljs-dark .hljs-quote,
.hljs-dark .hljs-name,
.hljs-dark .hljs-selector-id,
.hljs-dark .hljs-selector-class {
    color: #8be9fd;
}

.hljs-dark .hljs-comment,
.hljs-dark .hljs-meta,
.hljs-dark .hljs-deletion {
    color: #6272a4;
}

.hljs-dark .hljs-attr,
.hljs-dark .hljs-attribute,
.hljs-dark .hljs-variable,
.hljs-dark .hljs-template-variable {
    color: #50fa7b;
}

.hljs-dark .hljs-number,
.hljs-dark .hljs-symbol {
    color: #f1fa8c;
}

.hljs-dark .hljs-function {
    color: #ff79c6;
}

.hljs-dark .hljs-params {
    color: #f8f8f2;
}

.hljs-dark .hljs-regexp {
    color: #f1fa8c;
}

.hljs-dark .hljs-title.function_ {
    color: #50fa7b;
}

.hljs-dark .hljs-subst {
    color: #f8f8f2;
}

.hljs-dark .hljs-operator {
    color: #ff79c6;
}

.hljs-dark .hljs-selector-tag {
    color: #ff79c6;
}

.hljs-dark .hljs-punctuation {
    color: #f8f8f2;
}

.hljs-dark .hljs-property {
    color: #8be9fd;
}

</style>

