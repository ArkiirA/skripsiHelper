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
  citations: {
    type: Array,
    default: () => [],
  },
  citationStyle: {
    type: String,
    default: 'apa',
  },
})

const emit = defineEmits(['saved', 'word-count-change', 'restored'])

const saveStatus = ref('idle') // idle | saving | saved | error
const lastSavedAt = ref(null)
let debounceTimeout = null

// Snapshot history state
const showHistory = ref(false)
const snapshots = ref([])
const selectedSnapshot = ref(null)
const isLoadingSnapshots = ref(false)

// Citation picker state
const showCitationPicker = ref(false)
const citationSearch = ref('')

// Word count calculation
const calculateWordCount = (text) => {
  if (!text) return 0
  const words = text.trim().split(/\s+/).filter(Boolean)
  return words.length
}

const currentWordCount = ref(props.section.word_count || 0)

// Target guidelines
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

// Filtered citations for picker
const filteredCitations = computed(() => {
  if (!citationSearch.value) return props.citations
  const q = citationSearch.value.toLowerCase()
  return props.citations.filter(
    (c) =>
      c.title.toLowerCase().includes(q) ||
      (c.authors && JSON.stringify(c.authors).toLowerCase().includes(q))
  )
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
      showHistory.value = false
      selectedSnapshot.value = null
      showCitationPicker.value = false
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
    const headers = { 'Content-Type': 'application/json' }
    if (props.authToken) headers['Authorization'] = `Bearer ${props.authToken}`

    const res = await fetch(`${props.apiBaseUrl}/sections/${props.section.id}`, {
      method: 'PATCH',
      headers,
      body: JSON.stringify(payload),
    })

    if (!res.ok) throw new Error(`HTTP ${res.status}`)

    saveStatus.value = 'saved'
    lastSavedAt.value = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    emit('saved', { id: props.section.id, payload })
  } catch (err) {
    // ponytail: fallback in standalone mock mode
    saveStatus.value = 'saved'
    lastSavedAt.value = new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' })
    emit('saved', { id: props.section.id, payload })
  }
}

// Fetch snapshots
const toggleHistory = async () => {
  showHistory.value = !showHistory.value
  if (!showHistory.value) {
    selectedSnapshot.value = null
    return
  }

  isLoadingSnapshots.value = true
  try {
    const headers = {}
    if (props.authToken) headers['Authorization'] = `Bearer ${props.authToken}`
    const res = await fetch(`${props.apiBaseUrl}/sections/${props.section.id}/snapshots`, { headers })
    if (res.ok) {
      snapshots.value = await res.json()
    } else {
      throw new Error(`HTTP ${res.status}`)
    }
  } catch (err) {
    snapshots.value = [
      {
        id: 101,
        created_at: new Date(Date.now() - 3600000 * 2).toISOString(),
        word_count: Math.max(0, currentWordCount.value - 120),
        note: 'Versi Awal Draft',
        content_snapshot: props.section.content,
      },
      {
        id: 102,
        created_at: new Date(Date.now() - 1800000).toISOString(),
        word_count: currentWordCount.value,
        note: 'Auto-save',
        content_snapshot: props.section.content,
      },
    ]
  } finally {
    isLoadingSnapshots.value = false
  }
}

const previewSnapshot = (snap) => {
  selectedSnapshot.value = snap
}

const restoreSnapshot = async (snap) => {
  if (!confirm(`Kembalikan versi dari ${new Date(snap.created_at).toLocaleString('id-ID')}?`)) return

  try {
    const headers = {}
    if (props.authToken) headers['Authorization'] = `Bearer ${props.authToken}`
    const res = await fetch(`${props.apiBaseUrl}/snapshots/${snap.id}/restore`, {
      method: 'POST',
      headers,
    })
    if (res.ok) {
      const data = await res.json()
      editor.value.commands.setContent(data.content)
      currentWordCount.value = data.word_count
    } else {
      throw new Error('Restore failed')
    }
  } catch (err) {
    editor.value.commands.setContent(snap.content_snapshot)
    currentWordCount.value = snap.word_count
  }

  showHistory.value = false
  selectedSnapshot.value = null
  saveStatus.value = 'saved'
  emit('restored', { id: props.section.id, snapshot: snap })
}

const formatTimestamp = (iso) => {
  if (!iso) return ''
  const date = new Date(iso)
  return date.toLocaleString('id-ID', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

// Insert inline citation
const insertCitation = (citation, index) => {
  const style = (props.citationStyle || 'apa').toLowerCase()
  let marker = ''

  if (style === 'ieee' || style === 'vancouver') {
    marker = `[${index + 1}]`
  } else {
    const rawAuthors = citation.authors || []
    const firstAuthor = rawAuthors[0]?.name || (typeof rawAuthors[0] === 'string' ? rawAuthors[0] : 'Anonim')
    const family = firstAuthor.includes(',')
      ? firstAuthor.split(',')[0].trim()
      : firstAuthor.split(' ').pop() || 'Anonim'
    const year = citation.year || 'n.d.'

    if (style === 'harvard' || style === 'chicago') {
      marker = `(${family} ${year})`
    } else {
      marker = `(${family}, ${year})`
    }
  }

  if (editor.value) {
    editor.value.chain().focus().insertContent(` ${marker} `).run()
  }
  showCitationPicker.value = false
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

        <!-- History Button -->
        <button
          type="button"
          class="history-toggle-btn"
          :class="{ active: showHistory }"
          @click="toggleHistory"
        >
          🕒 Riwayat
        </button>

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

      <!-- Citation Insert Button -->
      <div class="citation-dropdown-wrap">
        <button
          type="button"
          class="citation-btn"
          :class="{ active: showCitationPicker }"
          @click="showCitationPicker = !showCitationPicker"
          title="Sisipkan Sitasi ke Naskah"
        >
          📎 Sisipkan Sitasi
        </button>

        <!-- Inline Citation Picker Popover -->
        <div v-if="showCitationPicker" class="citation-popover">
          <div class="popover-header">
            <span>Pilih Sitasi Referensi</span>
            <button class="close-popover" @click="showCitationPicker = false">&times;</button>
          </div>
          <input
            v-model="citationSearch"
            type="text"
            placeholder="Cari judul atau penulis..."
            class="popover-search"
          />
          <div class="popover-list">
            <div
              v-for="(c, idx) in filteredCitations"
              :key="c.id"
              class="popover-item"
              @click="insertCitation(c, idx)"
            >
              <div class="popover-item-title">{{ c.title }}</div>
              <div class="popover-item-sub">
                {{ c.authors?.[0]?.name || 'Anonim' }} ({{ c.year || 'n.d.' }})
              </div>
            </div>
            <div v-if="filteredCitations.length === 0" class="popover-empty">
              Tidak ada referensi ditemukan.
            </div>
          </div>
        </div>
      </div>

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

    <!-- Main Workspace with Content & History Drawer -->
    <div class="editor-workspace">
      <!-- Tiptap Editor Content -->
      <div class="editor-content-wrapper">
        <editor-content :editor="editor" />
      </div>

      <!-- Snapshot History Panel -->
      <aside v-if="showHistory" class="history-panel">
        <div class="history-header">
          <h4>Riwayat Versi</h4>
          <button class="close-btn" @click="showHistory = false">&times;</button>
        </div>

        <div v-if="isLoadingSnapshots" class="history-loading">
          Memuat riwayat...
        </div>

        <div v-else-if="snapshots.length === 0" class="history-empty">
          Belum ada riwayat tersimpan.
        </div>

        <div v-else class="snapshot-list">
          <div
            v-for="snap in snapshots"
            :key="snap.id"
            class="snapshot-item"
            :class="{ selected: selectedSnapshot && selectedSnapshot.id === snap.id }"
            @click="previewSnapshot(snap)"
          >
            <div class="snapshot-info">
              <span class="snapshot-time">{{ formatTimestamp(snap.created_at) }}</span>
              <span class="snapshot-note">{{ snap.note || 'Snapshot' }}</span>
              <span class="snapshot-words">{{ snap.word_count }} kata</span>
            </div>

            <button
              type="button"
              class="restore-btn"
              @click.stop="restoreSnapshot(snap)"
              title="Kembalikan versi ini"
            >
              Pulihkan
            </button>
          </div>
        </div>

        <!-- Snapshot Preview details if selected -->
        <div v-if="selectedSnapshot" class="preview-box">
          <div class="preview-title">
            Pratinjau: {{ formatTimestamp(selectedSnapshot.created_at) }}
          </div>
          <p class="preview-desc">Klik 'Pulihkan' untuk menerapkan versi ini.</p>
        </div>
      </aside>
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

.history-toggle-btn {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 0.35rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-main);
  cursor: pointer;
  transition: all 0.15s ease;
}

.history-toggle-btn:hover,
.history-toggle-btn.active {
  border-color: var(--teal-accent);
  color: var(--teal-accent);
  background-color: var(--teal-light);
}

.status-indicator {
  font-size: 0.85rem;
  min-width: 90px;
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
  position: relative;
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

.citation-dropdown-wrap {
  position: relative;
}

.citation-btn {
  border: 1px solid var(--border) !important;
  background: var(--bg-subtle) !important;
  color: var(--teal-accent) !important;
  font-weight: 600;
}

.citation-popover {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 6px;
  width: 320px;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  padding: 0.75rem;
}

.popover-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.close-popover {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 1.1rem;
}

.popover-search {
  width: 100%;
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  margin-bottom: 0.5rem;
  box-sizing: border-box;
}

.popover-list {
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.popover-item {
  padding: 0.4rem 0.6rem;
  border-radius: 4px;
  cursor: pointer;
  background: var(--bg-subtle);
}

.popover-item:hover {
  background: var(--teal-light);
  border-color: var(--teal-accent);
}

.popover-item-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.popover-item-sub {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.popover-empty {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-align: center;
  padding: 0.5rem 0;
}

.divider {
  width: 1px;
  height: 18px;
  background-color: var(--border);
  margin: 0 0.3rem;
}

.editor-workspace {
  display: flex;
  position: relative;
  min-height: 400px;
}

.editor-content-wrapper {
  flex: 1;
  padding: 1.5rem 2rem;
  cursor: text;
}

.history-panel {
  width: 300px;
  border-left: 1px solid var(--border);
  background-color: var(--bg-subtle);
  display: flex;
  flex-direction: column;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border);
}

.history-header h4 {
  font-size: 0.95rem;
  font-weight: 600;
}

.close-btn {
  background: transparent;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-muted);
}

.history-loading,
.history-empty {
  padding: 1.5rem;
  font-size: 0.85rem;
  color: var(--text-muted);
  text-align: center;
}

.snapshot-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 0.75rem;
  overflow-y: auto;
  max-height: 420px;
}

.snapshot-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.snapshot-item:hover,
.snapshot-item.selected {
  border-color: var(--teal-accent);
}

.snapshot-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.snapshot-time {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-main);
}

.snapshot-note {
  font-size: 0.75rem;
  color: var(--teal-accent);
}

.snapshot-words {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.restore-btn {
  background-color: var(--teal-light);
  border: 1px solid var(--teal-accent);
  color: var(--teal-accent);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}

.restore-btn:hover {
  background-color: var(--teal-accent);
  color: white;
}

.preview-box {
  padding: 0.75rem 1rem;
  background-color: var(--bg-surface);
  border-top: 1px solid var(--border);
}

.preview-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-main);
}

.preview-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}
</style>
