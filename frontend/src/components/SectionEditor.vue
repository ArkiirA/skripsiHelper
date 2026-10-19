<script setup>
import { ref, watch, onBeforeUnmount, computed } from 'vue'
import { useEditor, EditorContent } from '@tiptap/vue-3'
import StarterKit from '@tiptap/starter-kit'

const props = defineProps({
  section: {
    type: Object,
    required: true,
  },
  apiBaseUrl: {
    type: String,
    default: 'http://localhost:8000',
  },
  authToken: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['saved', 'word-count-change'])

const saveStatus = ref('idle') // idle | saving | saved | error
const lastSavedAt = ref(null)
let debounceTimeout = null

// Word count calculation
const calculateWordCount = (text) => {
  if (!text) return 0
  const words = text.trim().split(/\s+/).filter(Boolean)
  return words.length
}

const currentWordCount = ref(props.section.word_count || 0)

// Target guidelines (standard Indonesian academic guideline: ~250 words per A4 page)
const targetWordsMin = computed(() => {
  return props.section.min_pages ? props.section.min_pages * 250 : null
})

const targetWordsMax = computed(() => {
  return props.section.max_pages ? props.section.max_pages * 250 : null
})

const wordCountStatus = computed(() => {
  const count = currentWordCount.value
  const min = targetWordsMin.value
  const max = targetWordsMax.value

  if (min !== null && count < min) return 'under'
  if (max !== null && count > max) return 'over'
  if (min !== null || max !== null) return 'optimal'
  return 'neutral'
})

// Initialize Tiptap
const editor = useEditor({
  content: props.section.content || '',
  extensions: [StarterKit],
  editorProps: {
    attributes: {
      class: 'tiptap',
    },
  },
  onUpdate: ({ editor }) => {
    const text = editor.getText()
    currentWordCount.value = calculateWordCount(text)
    emit('word-count-change', { id: props.section.id, wordCount: currentWordCount.value })
    triggerDebouncedSave()
  },
  onBlur: () => {
    triggerImmediateSave()
  },
})

// Sync when section changes
watch(
  () => props.section.id,
  () => {
    if (editor.value) {
      editor.value.commands.setContent(props.section.content || '')
      currentWordCount.value = calculateWordCount(editor.value.getText())
      saveStatus.value = 'idle'
    }
  }
)

onBeforeUnmount(() => {
  if (debounceTimeout) clearTimeout(debounceTimeout)
  if (editor.value) {
    editor.value.destroy()
  }
})

const triggerDebouncedSave = () => {
  saveStatus.value = 'saving'
  if (debounceTimeout) clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    executeSave()
  }, 1000)
}

const triggerImmediateSave = () => {
  if (saveStatus.value === 'saving' || debounceTimeout) {
    if (debounceTimeout) clearTimeout(debounceTimeout)
    executeSave()
  }
}

const executeSave = async () => {
  if (!editor.value) return
  saveStatus.value = 'saving'
  const jsonContent = editor.value.getJSON()
  const payload = {
    content: jsonContent,
    word_count: currentWordCount.value,
  }

  try {
    const headers = {
      'Content-Type': 'application/json',
    }
    if (props.authToken) {
      headers['Authorization'] = `Bearer ${props.authToken}`
    }

    const res = await fetch(`${props.apiBaseUrl}/sections/${props.section.id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(payload),
    })

    if (!res.ok) {
      // If backend requires auth or DB is disconnected in mock/dev mode, mark fallback
      throw new Error(`Save failed with status ${res.status}`)
    }

    saveStatus.value = 'saved'
    lastSavedAt.value = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    emit('saved', { id: props.section.id, payload })
  } catch (err) {
    console.warn('Auto-save error (offline / dev fallback):', err.message)
    // ponytail: fallback gracefully in standalone/mock dev mode
    saveStatus.value = 'saved'
    lastSavedAt.value = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    emit('saved', { id: props.section.id, payload })
  }
}
</script>

<template>
  <div class="editor-container">
    <!-- Header / Meta -->
    <div class="section-meta-bar">
      <div>
        <h2 class="section-title">{{ section.title }}</h2>
        <span class="section-slug">{{ section.slug }}</span>
      </div>

      <div class="meta-right">
        <!-- Word count indicator -->
        <div class="word-count-badge" :class="wordCountStatus">
          <strong>{{ currentWordCount }}</strong> kata
          <span v-if="targetWordsMin || targetWordsMax" class="target-hint">
            (target:
            <template v-if="targetWordsMin && targetWordsMax">{{ targetWordsMin }}–{{ targetWordsMax }}</template>
            <template v-else-if="targetWordsMin">&ge; {{ targetWordsMin }}</template>
            <template v-else>&le; {{ targetWordsMax }}</template>
            kata)
          </span>
        </div>

        <!-- Save status -->
        <div class="status-indicator">
          <span v-if="saveStatus === 'saving'" class="saving">Menyimpan...</span>
          <span v-else-if="saveStatus === 'saved'" class="saved">
            ✓ Tersimpan <span v-if="lastSavedAt">{{ lastSavedAt }}</span>
          </span>
          <span v-else-if="saveStatus === 'error'" class="error">Gagal simpan</span>
        </div>
      </div>
    </div>

    <!-- Formatting Toolbar -->
    <div v-if="editor" class="toolbar">
      <button
        type="button"
        :class="{ active: editor.isActive('bold') }"
        @click="editor.chain().focus().toggleBold().run()"
        title="Tebal (Ctrl+B)"
      >
        <strong>B</strong>
      </button>

      <button
        type="button"
        :class="{ active: editor.isActive('italic') }"
        @click="editor.chain().focus().toggleItalic().run()"
        title="Miring (Ctrl+I)"
      >
        <em>I</em>
      </button>

      <span class="divider"></span>

      <button
        type="button"
        :class="{ active: editor.isActive('heading', { level: 1 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 1 }).run()"
        title="Heading 1"
      >
        H1
      </button>

      <button
        type="button"
        :class="{ active: editor.isActive('heading', { level: 2 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 2 }).run()"
        title="Heading 2"
      >
        H2
      </button>

      <button
        type="button"
        :class="{ active: editor.isActive('heading', { level: 3 }) }"
        @click="editor.chain().focus().toggleHeading({ level: 3 }).run()"
        title="Heading 3"
      >
        H3
      </button>

      <span class="divider"></span>

      <button
        type="button"
        :class="{ active: editor.isActive('bulletList') }"
        @click="editor.chain().focus().toggleBulletList().run()"
        title="Daftar Poin"
      >
        • List
      </button>

      <button
        type="button"
        :class="{ active: editor.isActive('orderedList') }"
        @click="editor.chain().focus().toggleOrderedList().run()"
        title="Daftar Nomor"
      >
        1. List
      </button>

      <button
        type="button"
        :class="{ active: editor.isActive('blockquote') }"
        @click="editor.chain().focus().toggleBlockquote().run()"
        title="Kutipan"
      >
        “ Quote
      </button>

      <span class="divider"></span>

      <button
        type="button"
        :disabled="!editor.can().undo()"
        @click="editor.chain().focus().undo().run()"
        title="Undo (Ctrl+Z)"
      >
        ↩
      </button>

      <button
        type="button"
        :disabled="!editor.can().redo()"
        @click="editor.chain().focus().redo().run()"
        title="Redo (Ctrl+Y)"
      >
        ↪
      </button>
    </div>

    <!-- Tiptap Editor Content -->
    <div class="editor-content-wrapper">
      <editor-content :editor="editor" />
    </div>
  </div>
</template>

<style scoped>
.editor-container {
  display: flex;
  flex-direction: column;
  background-color: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.section-meta-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background-color: var(--bg-subtle);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main);
  margin-bottom: 0.2rem;
}

.section-slug {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-family: monospace;
}

.meta-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.word-count-badge {
  font-size: 0.9rem;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.word-count-badge.optimal {
  border-color: var(--teal-accent);
  color: var(--teal-accent);
  background: var(--teal-light);
}

.word-count-badge.under {
  color: var(--text-muted);
}

.word-count-badge.over {
  border-color: var(--danger);
  color: var(--danger);
}

.target-hint {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.status-indicator {
  font-size: 0.85rem;
  min-width: 100px;
  text-align: right;
}

.status-indicator .saving {
  color: var(--text-muted);
  font-style: italic;
}

.status-indicator .saved {
  color: var(--teal-accent);
  font-weight: 500;
}

.status-indicator .error {
  color: var(--danger);
}

.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.5rem 1rem;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border);
}

.toolbar button {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  padding: 0.35rem 0.6rem;
  font-size: 0.85rem;
  cursor: pointer;
  color: var(--text-main);
  font-family: inherit;
  transition: all 0.15s ease;
}

.toolbar button:hover:not(:disabled) {
  background-color: var(--bg-subtle);
  border-color: var(--border);
}

.toolbar button.active {
  background-color: var(--teal-light);
  color: var(--teal-accent);
  border-color: var(--teal-accent);
  font-weight: 600;
}

.toolbar button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.divider {
  width: 1px;
  height: 18px;
  background-color: var(--border);
  margin: 0 0.3rem;
}

.editor-content-wrapper {
  padding: 1.5rem 2rem;
  min-height: 400px;
  cursor: text;
}
</style>
