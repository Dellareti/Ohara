<template>
  <div class="error-state" :class="[`error-${severity}`, { compact }]">
    <div class="error-content">
      <h3 v-if="!compact" class="error-title">
        {{ title || getDefaultTitle() }}
      </h3>
      
      <p class="error-message">
        {{ message }}
      </p>
      
      <div class="error-details" v-if="details && showDetails">
        <details>
          <summary>Technical details</summary>
          <pre>{{ details }}</pre>
        </details>
      </div>
    </div>

    <div class="error-actions" v-if="showActions">
      <button
        v-if="retryable && onRetry"
        @click="handleRetry"
        class="retry-btn"
        :disabled="retrying"
      >
        {{ retrying ? 'Retrying...' : 'Try again' }}
      </button>

      <button
        v-if="onDismiss"
        @click="onDismiss"
        class="dismiss-btn"
      >
        Dismiss
      </button>
      
      <slot name="actions"></slot>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { getErrorSeverity } from '../utils/errorUtils.js'

export default {
  name: 'ErrorState',
  props: {
    error: {
      type: [Error, String, Object],
      default: null
    },
    message: {
      type: String,
      required: true
    },
    title: {
      type: String,
      default: null
    },
    severity: {
      type: String,
      default: 'medium',
      validator: (value) => ['low', 'medium', 'high', 'critical'].includes(value)
    },
    retryable: {
      type: Boolean,
      default: false
    },
    compact: {
      type: Boolean,
      default: false
    },
    showDetails: {
      type: Boolean,
      default: false
    },
    showActions: {
      type: Boolean,
      default: true
    },
    onRetry: {
      type: Function,
      default: null
    },
    onDismiss: {
      type: Function,
      default: null
    }
  },
  setup(props) {
    const retrying = ref(false)
    
    const getDefaultTitle = () => {
      switch (props.severity) {
        case 'critical':
          return 'Critical Error'
        case 'high':
          return 'Important Error'
        case 'medium':
          return 'Error'
        case 'low':
          return 'Warning'
        default:
          return 'Error'
      }
    }
    
    const handleRetry = async () => {
      if (!props.onRetry || retrying.value) return
      
      retrying.value = true
      try {
        await props.onRetry()
      } catch (error) {
        console.error('Retry failed:', error)
      } finally {
        retrying.value = false
      }
    }
    
    const details = computed(() => {
      if (typeof props.error === 'string') return null
      if (!props.error) return null
      
      return {
        message: props.error.message,
        stack: props.error.stack,
        code: props.error.code,
        status: props.error.response?.status,
        timestamp: new Date().toISOString()
      }
    })
    
    return {
      retrying,
      details,
      getDefaultTitle,
      handleRetry
    }
  }
}
</script>

<style scoped>
.error-state {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background-color: #fef2f2;
  margin: 16px 0;
}

.error-state.compact {
  padding: 12px;
  margin: 8px 0;
}

.error-critical {
  background-color: #fef2f2;
  border-color: #fca5a5;
}

.error-high {
  background-color: #fffbeb;
  border-color: #fcd34d;
}

.error-medium {
  background-color: #fef2f2;
  border-color: #f87171;
}

.error-low {
  background-color: #f0f9ff;
  border-color: #7dd3fc;
}

.error-content {
  flex: 1;
  min-width: 0;
}

.error-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.error-message {
  margin: 0 0 12px 0;
  color: #4b5563;
  line-height: 1.5;
}

.error-details {
  margin-top: 8px;
}

.error-details summary {
  cursor: pointer;
  color: #6b7280;
  font-size: 14px;
}

.error-details pre {
  margin-top: 8px;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 4px;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.retry-btn, .dismiss-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn {
  background-color: #3b82f6;
  color: white;
}

.retry-btn:hover:not(:disabled) {
  background-color: #2563eb;
}

.retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.dismiss-btn {
  background-color: #6b7280;
  color: white;
}

.dismiss-btn:hover {
  background-color: #4b5563;
}

.compact .error-title {
  font-size: 16px;
  margin-bottom: 4px;
}

.compact .error-message {
  font-size: 14px;
  margin-bottom: 8px;
}

.compact .error-actions {
  gap: 6px;
}

.compact .retry-btn,
.compact .dismiss-btn {
  padding: 6px 12px;
  font-size: 13px;
}
</style>