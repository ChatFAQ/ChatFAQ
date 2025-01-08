<template>
    <div class="star-rating-wrapper">
        <div class="content">{{ props.data.content }}</div>
        <div class="star-rating" :class="{ 'dark-mode': store.darkMode }">
            <div 
                v-for="star in props.data.num_stars" 
                :key="star"
                class="star"
                :class="{
                    'filled': props.data.num_stars - star < rating,
                    'dark-mode': store.darkMode,
                    'disabled': rating > 0
                }"
                @click="rating === 0 && handleRating(props.data.num_stars - star + 1)"
            >
                ★
            </div>
        </div>
        <div v-if="props.data.explanation" class="explanation" :class="{ 'dark-mode': store.darkMode }">
            {{ props.data.explanation }}
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import { useGlobalStore } from "~/store";

const store = useGlobalStore();
const rating = ref(0);

const props = defineProps({
    data: {
        type: Object,
        required: true,
    },
    msgId: {
        type: String,
        required: true,
    },
});


async function handleRating(value) {
    rating.value = value;

    // Find the current message index
    const currentMsgIndex = store.messages.findIndex(msg => msg.id === props.msgId);
    // Search backwards from current message for the latest message/message_chunk
    const messageId = store.messages
        .slice(0, currentMsgIndex + 1)
        .reverse()
        .find(msg => msg.stack.some(stack => ['message', 'message_chunk', 'file_uploaded', 'file_download'].includes(stack.type)))?.id;

    if (!messageId) {
        console.error("No message found");
        return;
    }

    const feedbackData = {
        message: messageId,
        star_rating: rating.value,
        star_rating_max: props.data.num_stars,
    }

    const headers = { 'Content-Type': 'application/json' }
    if (store.authToken)
        headers.Authorization = `Token ${store.authToken}`;
    
    try {
        const response = await chatfaqFetch(store.chatfaqAPI + '/back/api/broker/user-feedback/', {
            method: 'POST',
            headers,
            body: JSON.stringify(feedbackData)
        });

        if (response.ok) {
            store.feedbackSent += 1;
            console.log("Feedback sent successfully");
        } else {
            console.error('Failed to send feedback:', response.status, response.statusText);
        }
    } catch (error) {
        console.error('Error sending feedback:', error);
    }

}
</script>

<style scoped lang="scss">
.star-rating-wrapper {
    display: flex;
    flex-direction: column;
    gap: 8px;

    .content {
        line-height: 1.4;
    }

    .star-rating {
        display: flex;
        gap: 4px;
        margin-top: 4px;
        flex-direction: row-reverse;
        justify-content: flex-end;

        .star {
            font-size: 24px;
            cursor: pointer;
            color: $chatfaq-star-rating-icon-color-light;
            opacity: 0.25;
            transition: color 0.2s ease, opacity 0.2s ease;

            &.filled {
                color: $chatfaq-star-rating-icon-color-light;
                opacity: 1;
            }

            /* Disable hover effects when the star is disabled */
            &:not(.disabled):hover,
            &:not(.disabled):hover ~ .star {
                color: inherit;
                opacity: 1;
            }
            
            /* Restrict hover-based color changes to non-disabled state */
            &:not(.disabled) {
                .star-rating:hover & {
                    color: $chatfaq-star-rating-icon-color-light;
                    opacity: 1;
                }

                .star-rating:hover & ~ .star {
                    color: inherit;
                    opacity: 0.25;
                }
            }

            &.dark-mode {
                color: $chatfaq-star-rating-icon-color-dark;

                &.filled {
                    color: $chatfaq-star-rating-icon-color-dark;
                }
            }

            &.disabled {
                cursor: default;
                
                &:hover {
                    color: inherit;
                    
                    &.filled {
                        color: $chatfaq-star-rating-icon-color-light;
                    }
                }
            }
        }
    }

    .explanation {
        font-size: 12px;
        color: $chatfaq-color-chatMessageReferenceTitle-text-light;
        font-style: italic;

        &.dark-mode {
            color: $chatfaq-color-chatMessageReferenceTitle-text-dark;
        }
    }
}
</style>