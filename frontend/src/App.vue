<script setup>
import { ref, computed } from 'vue'
import SectionEditor from './components/SectionEditor.vue'

// Outline items based on standard Indonesian skripsi preset (BAB I - BAB V)
const sections = ref([
  {
    id: 1,
    title: 'BAB I — 1.1 Latar Belakang Masalah',
    slug: 'bab-1-latar-belakang',
    order: 1,
    min_pages: 3,
    max_pages: 5,
    word_count: 320,
    content: {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'Perkembangan teknologi informasi dalam dekade terakhir telah mengubah pola interaksi akademik secara mendasar...',
            },
          ],
        },
      ],
    },
  },
  {
    id: 2,
    title: 'BAB I — 1.2 Rumusan Masalah',
    slug: 'bab-1-rumusan-masalah',
    order: 2,
    min_pages: 1,
    max_pages: 2,
    word_count: 95,
    content: {
      type: 'doc',
      content: [
        {
          type: 'paragraph',
          content: [
            {
              type: 'text',
              text: 'Berdasarkan latar belakang di atas, rumusan masalah dalam penelitian ini dirumuskan sebagai berikut:',
            },
          ],
        },
      ],
    },
  },
  {
    id: 3,
    title: 'BAB I — 1.3 Tujuan Penelitian',
    slug: 'bab-1-tujuan-penelitian',
    order: 3,
    min_pages: 1,
    max_pages: 2,
    word_count: 0,
    content: null,
  },
  {
    id: 4,
    title: 'BAB II — 2.1 Kajian Pustaka & Landasan Teori',
    slug: 'bab-2-landasan-teori',
    order: 4,
    min_pages: 8,
    max_pages: 15,
    word_count: 0,
    content: null,
  },
  {
    id: 5,
    title: 'BAB III — 3.1 Metode Penelitian',
    slug: 'bab-3-metode-penelitian',
    order: 5,
    min_pages: 5,
    max_pages: 10,
    word_count: 0,
    content: null,
  },
])

const activeSectionId = ref(1)

const activeSection = computed(() => {
  return sections.value.find((s) => s.id === activeSectionId.value) || sections.value[0]
})

const totalWordCount = computed(() => {
  return sections.value.reduce((acc, cur) => acc + (cur.word_count || 0), 0)
})

const handleWordCountChange = ({ id, wordCount }) => {
  const target = sections.value.find((s) => s.id === id)
  if (target) {
    target.word_count = wordCount
  }
}

const handleSaved = ({ id, payload }) => {
  const target = sections.value.find((s) => s.id === id)
  if (target) {
    target.content = payload.content
    target.word_count = payload.word_count
  }
}
</script>

<template>
  <div class="app-layout">
    <!-- Top Navbar -->
    <header class="app-header">
      <div class="header-left">
        <h1 class="logo">Skripsi<span>Helper</span></h1>
        <span class="project-title">Pengaruh AI terhadap Produktivitas Mahasiswa Tingkat Akhir</span>
      </div>
      <div class="header-right">
        <div class="total-stats">
          Total Kata: <strong>{{ totalWordCount }}</strong>
        </div>
        <div class="user-pill">
          Mahasiswa UI (Hukum)
        </div>
      </div>
    </header>

    <!-- Main Workspace -->
    <div class="workspace-body">
      <!-- Outline Sidebar -->
      <aside class="outline-sidebar">
        <div class="sidebar-header">
          <h3>Sistematika Skripsi</h3>
          <span class="sub-label">Pedoman UI 2024</span>
        </div>

        <nav class="outline-list">
          <button
            v-for="sec in sections"
            :key="sec.id"
            class="outline-item"
            :class="{ active: sec.id === activeSectionId }"
            @click="activeSectionId = sec.id"
          >
            <div class="outline-title">{{ sec.title }}</div>
            <div class="outline-sub">
              <span>{{ sec.word_count || 0 }} kata</span>
              <span v-if="sec.min_pages" class="target">target {{ sec.min_pages }}–{{ sec.max_pages }} hal</span>
            </div>
          </button>
        </nav>
      </aside>

      <!-- Writing Pane -->
      <main class="editor-pane">
        <SectionEditor
          v-if="activeSection"
          :section="activeSection"
          @saved="handleSaved"
          @word-count-change="handleWordCountChange"
        />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-header {
  height: 58px;
  background-color: var(--bg-surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.logo {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--text-main);
  letter-spacing: -0.5px;
}

.logo span {
  color: var(--teal-accent);
}

.project-title {
  font-size: 0.95rem;
  color: var(--text-muted);
  border-left: 1px solid var(--border);
  padding-left: 1.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 480px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.total-stats {
  font-size: 0.9rem;
  color: var(--text-muted);
}

.total-stats strong {
  color: var(--teal-accent);
}

.user-pill {
  font-size: 0.8rem;
  background-color: var(--bg-subtle);
  border: 1px solid var(--border);
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  color: var(--text-main);
}

.workspace-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.outline-sidebar {
  width: 320px;
  background-color: var(--bg-surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 1.25rem 1.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
}

.sidebar-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-main);
}

.sidebar-header .sub-label {
  font-size: 0.8rem;
  color: var(--teal-accent);
  font-weight: 500;
}

.outline-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.outline-item {
  width: 100%;
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  cursor: pointer;
  font-family: inherit;
  transition: all 0.15s ease;
}

.outline-item:hover {
  background-color: var(--bg-subtle);
}

.outline-item.active {
  background-color: var(--teal-light);
  border-color: var(--teal-accent);
}

.outline-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 0.25rem;
}

.outline-item.active .outline-title {
  color: var(--teal-accent);
}

.outline-sub {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.editor-pane {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  background-color: var(--bg-primary);
}
</style>
