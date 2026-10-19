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
              text: 'Perkembangan teknologi kecerdasan buatan telah mengubah pola penyusunan karya ilmiah mahasiswa secara mendasar (Pratama, 2023). Integrasi automasi pengutipan meningkatkan kecepatan review literatur (Aditya & Lestari, 2022).',
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

// Citations collection for project
const citations = ref([
  {
    id: 1,
    title: 'Analisis Sentimen Twitter dengan BERT pada Mahasiswa Tingkat Akhir',
    authors: [{ name: 'Pratama, Budi' }],
    year: 2023,
    journal: 'Jurnal Sains Komputer & Informatika',
    volume: '10',
    issue: '2',
    pages: '100-112',
    doi: '10.1234/jsk.2023.01',
  },
  {
    id: 2,
    title: 'Penerapan Deep Learning pada Pengolahan Citra Medis dan Diagnostik',
    authors: [{ name: 'Aditya, Rizky' }, { name: 'Lestari, Dewi' }],
    year: 2022,
    journal: 'Informatika Indonesia',
    volume: '15',
    issue: '1',
    pages: '45-52',
    doi: '10.1234/ii.2022.02',
  },
  {
    id: 3,
    title: 'Tantangan Integritas Akademik di Era Generative AI pada Perguruan Tinggi',
    authors: [{ name: 'Sutanto, Hendra' }],
    year: 2024,
    journal: 'Jurnal Pendidikan Tinggi',
    volume: '8',
    issue: '3',
    pages: '210-225',
    doi: '10.5678/jpt.2024.08',
  },
])

// Selected view: section ID or 'bibliography'
const activeSectionId = ref(1)
const citationStyle = ref('apa')

const activeSection = computed(() => {
  if (activeSectionId.value === 'bibliography') return null
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

// Format bibliography list per style
const formattedBibliography = computed(() => {
  const style = citationStyle.value.toLowerCase()
  let list = [...citations.value]

  if (style === 'apa' || style === 'harvard' || style === 'chicago') {
    list.sort((a, b) => {
      const nameA = a.authors?.[0]?.name || ''
      const nameB = b.authors?.[0]?.name || ''
      return nameA.localeCompare(nameB)
    })
  }

  return list.map((c, idx) => {
    const authors = c.authors || []
    const title = c.title || 'Tanpa Judul'
    const year = c.year || 'n.d.'
    const journal = c.journal
    const doi = c.doi
    const vol = c.volume
    const iss = c.issue
    const pgs = c.pages

    let formatted = ''
    let marker = ''

    if (style === 'ieee') {
      const authStr = authors.map((a) => a.name.split(',').reverse().join(' ').trim()).join(', ')
      formatted = `[${idx + 1}] ${authStr}, "${title}," ${journal ? journal + ',' : ''} vol. ${vol || 1}, no. ${iss || 1}, pp. ${pgs || '-'}, ${year}.`
      marker = `[${idx + 1}]`
    } else if (style === 'vancouver') {
      const authStr = authors.map((a) => a.name.split(',')[0]).join(', ')
      formatted = `${idx + 1}. ${authStr}. ${title}. ${journal ? journal + '.' : ''} ${year};${vol || ''}(${iss || ''}):${pgs || ''}.`
      marker = `[${idx + 1}]`
    } else if (style === 'harvard') {
      const authStr = authors.map((a) => a.name).join(', ')
      formatted = `${authStr}, ${year}. ${title}. ${journal ? journal + ', ' : ''}${vol ? vol + '(' + iss + '), ' : ''}pp.${pgs || '-'}.`
      const lead = authors[0]?.name.split(',')[0] || 'Anonim'
      marker = `(${lead} ${year})`
    } else if (style === 'chicago') {
      const authStr = authors.map((a) => a.name).join(', ')
      formatted = `${authStr}. ${year}. "${title}." ${journal ? journal + ' ' : ''}${vol || ''}, no. ${iss || ''}: ${pgs || ''}.`
      const lead = authors[0]?.name.split(',')[0] || 'Anonim'
      marker = `(${lead} ${year})`
    } else {
      // APA 7th
      let authStr = 'Anonim'
      if (authors.length === 1) authStr = authors[0].name
      else if (authors.length === 2) authStr = `${authors[0].name} & ${authors[1].name}`
      else if (authors.length > 2) authStr = `${authors[0].name} et al.`

      formatted = `${authStr} (${year}). ${title}.${journal ? ' ' + journal + '.' : ''}${doi ? ' https://doi.org/' + doi : ''}`
      const lead = authors[0]?.name.split(',')[0] || 'Anonim'
      marker = `(${lead}, ${year})`
    }

    return {
      id: c.id,
      index: idx + 1,
      marker,
      formatted,
    }
  })
})

const copyBibliography = () => {
  const text = formattedBibliography.value.map((b) => b.formatted).join('\n\n')
  navigator.clipboard.writeText(text)
  alert('Daftar pustaka disalin ke clipboard!')
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

          <!-- Daftar Pustaka Item -->
          <button
            type="button"
            class="outline-item bibliography-nav-item"
            :class="{ active: activeSectionId === 'bibliography' }"
            @click="activeSectionId = 'bibliography'"
          >
            <div class="outline-title">📚 Daftar Pustaka</div>
            <div class="outline-sub">
              <span>{{ citations.length }} referensi</span>
              <span class="target">{{ citationStyle.toUpperCase() }}</span>
            </div>
          </button>
        </nav>
      </aside>

      <!-- Main Pane -->
      <main class="editor-pane">
        <!-- Editor View -->
        <SectionEditor
          v-if="activeSection"
          :section="activeSection"
          :citations="citations"
          :citation-style="citationStyle"
          @saved="handleSaved"
          @word-count-change="handleWordCountChange"
        />

        <!-- Bibliography View -->
        <div v-else-if="activeSectionId === 'bibliography'" class="bibliography-view">
          <div class="bib-header">
            <div>
              <h2>Daftar Pustaka</h2>
              <p class="bib-subtitle">Daftar referensi otomatis terformat sesuai pedoman penulisan.</p>
            </div>

            <div class="bib-actions">
              <!-- Style Switcher -->
              <div class="style-selector">
                <label for="style-select">Gaya Sitasi:</label>
                <select id="style-select" v-model="citationStyle">
                  <option value="apa">APA 7th Edition</option>
                  <option value="ieee">IEEE</option>
                  <option value="vancouver">Vancouver</option>
                  <option value="harvard">Harvard</option>
                  <option value="chicago">Chicago (Author-Date)</option>
                </select>
              </div>

              <button type="button" class="copy-btn" @click="copyBibliography">
                📋 Salin Semua
              </button>
            </div>
          </div>

          <div class="bib-card">
            <div v-if="formattedBibliography.length === 0" class="bib-empty">
              Belum ada referensi ditambahkan.
            </div>

            <div v-else class="bib-entries">
              <div
                v-for="b in formattedBibliography"
                :key="b.id"
                class="bib-entry-row"
              >
                <span class="bib-marker">{{ b.marker }}</span>
                <p class="bib-text">{{ b.formatted }}</p>
              </div>
            </div>
          </div>
        </div>
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

.bibliography-nav-item {
  border-top: 1px dashed var(--border);
  margin-top: 0.5rem;
  padding-top: 0.8rem;
}

.editor-pane {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  background-color: var(--bg-primary);
}

/* Bibliography View */
.bibliography-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.bib-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.bib-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
}

.bib-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.bib-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.style-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.style-selector select {
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--bg-surface);
  color: var(--text-main);
  font-family: inherit;
  font-weight: 600;
}

.copy-btn {
  background-color: var(--teal-accent);
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.copy-btn:hover {
  opacity: 0.9;
}

.bib-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.bib-empty {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}

.bib-entries {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.bib-entry-row {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  line-height: 1.6;
}

.bib-marker {
  font-weight: 700;
  color: var(--teal-accent);
  font-size: 0.85rem;
  min-width: 90px;
}

.bib-text {
  flex: 1;
  font-size: 0.95rem;
  color: var(--text-main);
}
</style>
