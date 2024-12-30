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
});

console.log("props", props);

function handleRating(value) {
    rating.value = value;

    console.log("rating", rating.value);
    
    // const m = {
    //     "sender": {
    //         "type": "human",
    //         "platform": "WS",
    //     },
    //     "stack": [{
    //         "type": "star_rating_response",
    //         "payload": {
    //             "rating": value
    //         },
    //     }],
    //     "stack_id": "0",
    //     "stack_group_id": "0",
    //     "last": true,
    // };
    
    // if (store.userId !== undefined) {
    //     m["sender"]["id"] = store.userId;
    // }

    // store.messagesToBeSent.push(m);
    // store.messagesToBeSentSignal += 1;
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
            color: $chatfaq-color-chatMessageReference-background-light;
            transition: color 0.2s ease;

            &.filled {
                color: #FFD700;
            }

            /* Disable hover effects when the star is disabled */
            &:not(.disabled):hover,
            &:not(.disabled):hover ~ .star {
                color: inherit;
            }
            
            /* Restrict hover-based color changes to non-disabled state */
            &:not(.disabled) {
                .star-rating:hover & {
                    color: #FFD700;
                }

                .star-rating:hover & ~ .star {
                    color: inherit;
                }
            }

            &.dark-mode {
                color: $chatfaq-color-chatMessageReference-background-dark;

                &.filled {
                    color: #FFD700;
                }
            }

            &.disabled {
                cursor: default;
                
                &:hover {
                    color: inherit;
                    
                    &.filled {
                        color: #FFD700;
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