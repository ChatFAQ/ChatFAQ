<template>
  <div class="tool-use-container" :class="{ 'dark-mode': store.darkMode, 'expanded': expanded }">
    <div class="tool-header" @click="toggleExpand">
      <div class="tool-info">
        <span class="tool-icon">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M6.5 10C8.43 10 10 8.43 10 6.5C10 4.57 8.43 3 6.5 3C4.57 3 3 4.57 3 6.5C3 8.43 4.57 10 6.5 10Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M9.14282 9.14282L12.9999 13.0001" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
        <span class="tool-name">{{ data.payload.name }}</span>
        <span v-if="isWaiting" class="tool-status waiting">
          <span class="waiting-dot"></span>
          <span class="waiting-dot"></span>
          <span class="waiting-dot"></span>
        </span>
        <span v-else-if="resultData" class="tool-status" :class="hasResult ? 'success' : 'error'">
          {{ hasResult ? '✓' : '✗' }}
        </span>
      </div>
      <span class="dropdown-icon" :class="{ 'expanded': expanded }">
        <ChevronDown />
      </span>
    </div>
    
    <div v-if="expanded" class="tool-details">
      <div class="tool-args">
        <pre>{{ JSON.stringify(data.payload.args, null, 2) }}</pre>
      </div>
      <div v-if="resultData" class="tool-result">
        <div class="result-header">
          <span class="result-label">Result:</span>
          <span v-if="hasResult" class="result-status success">✓ Success</span>
          <span v-else class="result-status error">✗ Error</span>
        </div>
        <TextMsgPiece 
          :data="formatToolResultData(resultData)" 
          :is-last="true" 
          :is-last-chunk="true"
        />
      </div>
      <div v-else class="tool-result pending">
        <span class="pending-indicator">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </span>
        <span class="pending-text">Waiting for result...</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useGlobalStore } from "~/store";
import TextMsgPiece from "~/components/chat/msgs/pieces/TextMsgPiece.vue";
import ChevronDown from "~/components/icons/ChevronDown.vue";

const props = defineProps({
  data: {
    type: Object,
    required: true
  },
  resultData: {
    type: Object,
    default: null
  }
});

const store = useGlobalStore();
const expanded = ref(false);

const hasResult = computed(() => {
  if (!props.resultData || !props.resultData.payload) return false;
  return props.resultData.payload.result !== undefined || props.resultData.payload.tool_result !== undefined;
});

const isWaiting = computed(() => {
  return !props.resultData;
});

function toggleExpand() {
  expanded.value = !expanded.value;
}

function formatToolResultData(resultData) {
  if (!resultData || !resultData.payload) return { payload: { content: 'No result data available' } };
  
  // The actual result is in tool_result for ToolResult instances
  const result = resultData.payload.result || resultData.payload.tool_result;
  
  return {
    ...resultData,
    payload: {
      content: typeof result === 'string' 
        ? result 
        : JSON.stringify(result, null, 2)
    }
  };
}

// Auto-expand when result arrives
watch(() => props.resultData, (newValue) => {
  if (newValue && !expanded.value) {
    expanded.value = true;
  }
}, { immediate: true });
</script>

<style scoped lang="scss">
.tool-use-container {
  width: 100%;
  border-radius: 6px;
  border: 1px solid rgba(0, 0, 0, 0.1);
  background-color: rgba(0, 0, 0, 0.02);
  margin-bottom: 8px;
  font-size: 0.9em;
  
  &.dark-mode {
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: $chatfaq-color-neutral-black;
  }
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
  
  &:hover {
    background-color: rgba(0, 0, 0, 0.05);
    
    .dark-mode & {
      background-color: rgba(255, 255, 255, 0.1);
    }
  }
}

.tool-info {
  display: flex;
  align-items: center;
}

.tool-icon {
  margin-right: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: $chatfaq-color-primary-800;
  
  .dark-mode & {
    color: $chatfaq-color-primary-500;
  }
  
  svg {
    width: 14px;
    height: 14px;
  }
}

.tool-name {
  font-weight: 500;
  color: $chatfaq-color-primary-800;
  margin-right: 8px;
  
  .dark-mode & {
    color: $chatfaq-color-primary-500;
  }
}

.tool-status {
  font-size: 0.8em;
  display: inline-flex;
  align-items: center;
  padding: 2px 6px;
  border-radius: 10px;
  
  &.success {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }
  
  &.error {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
  }
  
  &.waiting {
    display: inline-flex;
    align-items: center;
  }
}

.waiting-dot {
  width: 4px;
  height: 4px;
  background-color: currentColor;
  border-radius: 50%;
  margin: 0 2px;
  opacity: 0.7;
  animation: dotPulse 1.5s infinite;
  
  &:nth-child(2) {
    animation-delay: 0.5s;
  }
  
  &:nth-child(3) {
    animation-delay: 1s;
  }
}

.dropdown-icon {
  transition: transform 0.3s ease;
  opacity: 0.6;
  
  &.expanded {
    transform: rotate(180deg);
  }
}

.tool-details {
  padding: 0 12px 12px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  
  .dark-mode & {
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
}

.tool-args {
  background-color: rgba(0, 0, 0, 0.03);
  border-radius: 4px;
  padding: 8px;
  margin: 8px 0;
  font-family: monospace;
  font-size: 0.85em;
  max-height: 200px;
  overflow: auto;
  
  .dark-mode & {
    background-color: rgba(0, 0, 0, 0.3);
  }
  
  pre {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

.tool-result {
  margin-top: 12px;
  
  &.pending {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 12px;
    opacity: 0.7;
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.9em;
}

.result-label {
  font-weight: 500;
}

.result-status {
  &.success {
    color: #4caf50;
  }
  
  &.error {
    color: #f44336;
  }
}

/* Pending animation */
.pending-indicator {
  display: flex;
  align-items: center;
  margin-right: 8px;
  
  .dot {
    width: 6px;
    height: 6px;
    background-color: currentColor;
    border-radius: 50%;
    margin: 0 2px;
    opacity: 0.7;
    animation: dotPulse 1.5s infinite;
    
    &:nth-child(2) {
      animation-delay: 0.5s;
    }
    
    &:nth-child(3) {
      animation-delay: 1s;
    }
  }
}

@keyframes dotPulse {
  0%, 100% {
    opacity: 0.4;
    transform: scale(0.8);
  }
  50% {
    opacity: 1;
    transform: scale(1.2);
  }
}
</style> 