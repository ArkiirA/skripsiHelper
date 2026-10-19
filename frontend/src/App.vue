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

// Konsultasi Logs (Advisor notes)
const konsultasiLogs = ref([
  {
    id: 1,
    date: '2024-10-12',
    notes: 'Perjelas batasan masalah di Bab 1. Jangan terlalu luas ke semua fakultas, fokus ke rumpun sains & teknologi.',
    is_resolved: false,
    created_at: '2024-10-12T10:30:00Z',
  },
  {
    id: 2,
    date: '2024-10-05',
    notes: 'Tambahkan minimal 5 referensi jurnal internasional bereputasi terbitan 3 tahun terakhir.',
    is_resolved: true,
    resolved_at: '2024-10-08T14:20:00Z',
    created_at: '2024-10-05T09:15:00Z',
  },
])

const newLogNotes = ref('')
const newLogDate = ref(new Date().toISOString().slice(0, 10))

// Selected view: section ID, 'bibliography', or 'konsultasi'
const activeSectionId = ref(1)
const citationStyle = ref('apa')

const activeSection = computed(() => {
  if (typeof activeSectionId.value !== 'number') return null
  return sections.value.find((s) => s.id === activeSectionId.value) || sections.value[0]
})

const totalWordCount = computed(() => {
  return sections.value.reduce((acc, cur) => acc + (cur.word_count || 0), 0)
})

const unresolvedKonsultasiCount = computed(() => {
  return konsultasiLogs.value.filter((k) => !k.is_resolved).length
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

// Add new konsultasi log
const addKonsultasiLog = () => {
  if (!newLogNotes.value.trim()) return
  konsultasiLogs.value.unshift({
    id: Date.now(),
    date: newLogDate.value,
    notes: newLogNotes.value.trim(),
    is_resolved: false,
    created_at: new Date().toISOString(),
  })
  newLogNotes.value = ''
}

// Toggle resolved status
const toggleLogResolved = (log) => {
  log.is_resolved = !log.is_resolved
  log.resolved_at = log.is_resolved ? new Date().toISOString() : null
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

        <button
          v-if="unresolvedKonsultasiCount > 0"
          type="button"
          class="reminder-pill"
          @click="activeSectionId = 'konsultasi'"
        >
          ⚠️ {{ unresolvedKonsultasiCount }} Catatan Dosen Belum Selesai
        </button>

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
            class="outline-item nav-extra-item"
            :class="{ active: activeSectionId === 'bibliography' }"
            @click="activeSectionId = 'bibliography'"
          >
            <div class="outline-title">📚 Daftar Pustaka</div>
            <div class="outline-sub">
              <span>{{ citations.length }} referensi</span>
              <span class="target">{{ citationStyle.toUpperCase() }}</span>
            </div>
          </button>

          <!-- Catatan Bimbingan Item -->
          <button
            type="button"
            class="outline-item nav-extra-item"
            :class="{ active: activeSectionId === 'konsultasi' }"
            @click="activeSectionId = 'konsultasi'"
          >
            <div class="outline-title">📝 Catatan Bimbingan</div>
            <div class="outline-sub">
              <span>{{ konsultasiLogs.length }} sesi</span>
              <span v-if="unresolvedKonsultasiCount > 0" class="badge-unresolved">
                {{ unresolvedKonsultasiCount }} pending
              </span>
              <span v-else class="target">Semua selesai</span>
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
        <div v-else-if="activeSectionId === 'bibliography'" class="panel-view">
          <div class="panel-header">
            <div>
              <h2>Daftar Pustaka</h2>
              <p class="panel-subtitle">Daftar referensi otomatis terformat sesuai pedoman penulisan.</p>
            </div>

            <div class="panel-actions">
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

              <button type="button" class="btn-primary" @click="copyBibliography">
                📋 Salin Semua
              </button>
            </div>
          </div>

          <div class="content-card">
            <div v-if="formattedBibliography.length === 0" class="empty-state">
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

        <!-- Konsultasi Log View -->
        <div v-else-if="activeSectionId === 'konsultasi'" class="panel-view">
          <div class="panel-header">
            <div>
              <h2>Catatan Bimbingan (Konsultasi Log)</h2>
              <p class="panel-subtitle">Catat arahan dan revisi dari dosen pembimbing.</p>
            </div>
          </div>

          <!-- Unresolved Reminder Banner -->
          <div v-if="unresolvedKonsultasiCount > 0" class="reminder-banner">
            <strong>⚠️ Ada {{ unresolvedKonsultasiCount }} revisi belum diselesaikan:</strong>
            Periksa catatan di bawah dan centang status setelah diperbaiki pada naskah.
          </div>

          <!-- Add Note Box -->
          <div class="content-card new-log-box">
            <h3>+ Tambah Catatan Sesi Bimbingan</h3>
            <div class="new-log-form">
              <div class="form-row">
                <label>Tanggal Bimbingan:</label>
                <input v-model="newLogDate" type="date" class="form-input" />
              </div>
              <textarea
                v-model="newLogNotes"
                placeholder="Tuliskan arahan, masukan, atau poin revisi dari dosen..."
                rows="3"
                class="form-textarea"
              ></textarea>
              <button type="button" class="btn-primary" @click="addKonsultasiLog">
                Simpan Catatan
              </button>
            </div>
          </div>

          <!-- Log Timeline -->
          <div class="content-card">
            <h3>Daftar Sesi Bimbingan ({{ konsultasiLogs.length }})</h3>

            <div v-if="konsultasiLogs.length === 0" class="empty-state">
              Belum ada catatan bimbingan tersimpan.
            </div>

            <div v-else class="log-timeline">
              <div
                v-for="log in konsultasiLogs"
                :key="log.id"
                class="log-card"
                :class="{ resolved: log.is_resolved }"
              >
                <div class="log-card-header">
                  <span class="log-date">📅 {{ log.date }}</span>
                  <button
                    type="button"
                    class="status-toggle-btn"
                    :class="{ 'btn-resolved': log.is_resolved }"
                    @click="toggleLogResolved(log)"
                  >
                    {{ log.is_resolved ? '✓ Selesai' : '⏳ Belum Selesai' }}
                  </button>
                </div>
                <p class="log-notes">{{ log.notes }}</p>
                <div v-if="log.resolved_at" class="log-footer">
                  Diselesaikan pada {{ new Date(log.resolved_at).toLocaleDateString('id-ID') }}
                </div>
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

.reminder-pill {
  background-color: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  cursor: pointer;
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

.nav-extra-item {
  border-top: 1px dashed var(--border);
  margin-top: 0.5rem;
  padding-top: 0.8rem;
}

.badge-unresolved {
  color: #d97706;
  font-weight: 700;
}

.editor-pane {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 3rem;
  background-color: var(--bg-primary);
}

/* Panel Views (Bibliography / Konsultasi) */
.panel-view {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.panel-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
}

.panel-subtitle {
  font-size: 0.85rem;
  color: var(--text-muted);
  margin-top: 0.25rem;
}

.panel-actions {
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

.btn-primary {
  background-color: var(--teal-accent);
  color: white;
  border: none;
  padding: 0.45rem 0.9rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s ease;
}

.btn-primary:hover {
  opacity: 0.9;
}

.content-card {
  background-color: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.content-card h3 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--text-muted);
}

.reminder-banner {
  background-color: #fffbeb;
  border: 1px solid #fde68a;
  color: #92400e;
  padding: 1rem 1.25rem;
  border-radius: 8px;
  font-size: 0.9rem;
  line-height: 1.5;
}

.new-log-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-start;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.85rem;
}

.form-input {
  padding: 0.35rem 0.6rem;
  border: 1px solid var(--border);
  border-radius: 4px;
}

.form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-family: inherit;
  font-size: 0.9rem;
  box-sizing: border-box;
}

.log-timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.log-card {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1rem 1.25rem;
  background-color: var(--bg-surface);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.log-card.resolved {
  background-color: var(--bg-subtle);
  opacity: 0.8;
}

.log-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.log-date {
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text-muted);
}

.status-toggle-btn {
  padding: 0.25rem 0.6rem;
  border-radius: 9999px;
  border: 1px solid #fde68a;
  background-color: #fffbeb;
  color: #92400e;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.status-toggle-btn.btn-resolved {
  border-color: var(--teal-accent);
  background-color: var(--teal-light);
  color: var(--teal-accent);
}

.log-notes {
  font-size: 0.95rem;
  line-height: 1.5;
}

.log-footer {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Bibliography View */
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
