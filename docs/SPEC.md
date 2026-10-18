# SkripsiHelper — Product Spec

## Problem Statement

Indonesian university students face a painful journey from blank page to defensible skripsi draft. They must simultaneously manage document formatting (unique per university's pedoman), collect and format dozens of citations, track advisor revision requests across multiple bimbingan sessions, and structure their writing across mandatory chapters — all while using generic tools (Word, Google Docs) that know nothing about skripsi requirements. The result: formatting errors caught at the last minute, lost advisor feedback, citation style mistakes, and blank-page paralysis from not knowing where to start.

## Solution

SkripsiHelper is a web-based thesis-writing tool purpose-built for Indonesian students. It provides a structured writing environment shaped by their university's pedoman, with built-in citation management (upload PDFs, auto-extract metadata), a konsultasi log for tracking advisor feedback, AI-assisted research and writing aids, and one-click export to perfectly formatted DOCX and PDF. The app removes mechanical friction so students can focus on the intellectual work of their skripsi.

## User Stories

1. As a student, I want to sign in with my Google account, so that I don't need to create and remember another password.
2. As a student, I want to select my university's pedoman preset when creating a new skripsi project, so that my document structure and formatting are correct from the start.
3. As a student, I want to create a new pedoman preset by filling a structured form (margins, font, spacing, citation style, heading format, page numbering, required sections), so that my university's specific rules are captured.
4. As a student, I want my pedoman preset to be available to other students at my university, so that they don't have to re-enter the same rules.
5. As a student, I want to flag an inaccurate pedoman preset, so that incorrect formatting rules don't propagate.
6. As a student, I want to see how many other students use a pedoman preset, so that I can trust its accuracy.
7. As a student, I want to see my skripsi outline pre-populated with the required BABs and sub-sections from my pedoman (Latar Belakang, Rumusan Masalah, Tujuan, Manfaat, etc.), so that I know exactly what I need to write.
8. As a student, I want to write content in a rich text editor within each section, so that I can focus on one part at a time without blank-page paralysis.
9. As a student, I want the app to auto-save snapshots of each section, so that I can go back to what I had last week if my advisor wants the previous version.
10. As a student, I want to upload a PDF of a paper I'm citing and have the app automatically extract its citation metadata (title, authors, journal, year, DOI), so that I don't have to type it manually.
11. As a student, I want to paste a DOI as a fallback when auto-extraction fails, so that I can still add the citation quickly.
12. As a student, I want to manually enter citation details as a last resort, so that I can cite papers from Indonesian journals that lack DOIs.
13. As a student, I want my uploaded PDFs stored and accessible within the app, so that I can reference them later while writing.
14. As a student, I want citations in my daftar pustaka automatically formatted per my university's pedoman citation style (APA, IEEE, Vancouver, Chicago, or Harvard), so that I don't make formatting mistakes.
15. As a student, I want to insert a citation reference in my text and have it linked to an entry in my daftar pustaka, so that my references are consistent.
16. As a student, I want to record notes from each bimbingan session in a konsultasi log, so that I don't forget what my dosen pembimbing asked me to change.
17. As a student, I want to mark konsultasi log items as resolved, so that I can track what's done and what's still pending.
18. As a student, I want to receive reminders about unresolved konsultasi log items, so that I don't show up to the next bimbingan having forgotten something.
19. As a student, I want to see a progress dashboard showing word count per section vs. pedoman minimums, percentage of sections completed, and unresolved konsultasi items, so that I know where to focus my effort.
20. As a student, I want to export my skripsi as a DOCX formatted per my university's pedoman (correct margins, fonts, heading styles, page numbering with Roman numerals for front matter and Arabic for body, and a generated Table of Contents), so that my submission is format-compliant.
21. As a student, I want to export my skripsi as a PDF, so that I have a print-ready version.
22. As a student, I want AI to suggest an outline for my skripsi based on my research topic and pedoman, so that I have a starting structure to work from. (Premium)
23. As a student, I want AI to paraphrase selected text, so that I can rewrite passages in my own academic voice. (Premium)
24. As a student, I want AI to summarize an uploaded paper, so that I can quickly understand its key contributions before reading the full text. (Premium)
25. As a student, I want AI to check my writing for grammar and academic style in Bahasa Indonesia, so that my skripsi reads professionally. (Premium)
26. As a student, I want to search for academic papers by keyword, so that I can find sources relevant to my topic. (Premium)
27. As a student, I want to describe my research question in natural language and get relevant paper suggestions, so that I don't need to know the right keywords. (Premium)
28. As a student, I want to select a paper in my daftar pustaka and find similar papers, so that I can expand my literature review. (Premium)
29. As a student, I want AI to validate that my citation formatting matches my pedoman's citation style, so that I catch mistakes before submission. (Premium)
30. As a student, I want to use 5 AI actions per day for free, so that I can experience the value before paying.
31. As a student, I want to make a one-time payment (Rp 50.000) to unlock unlimited AI features for my skripsi project, so that I don't worry about daily limits during crunch time.
32. As a student, I want to pay via QRIS, GoPay, OVO, or bank transfer, so that I can use the payment method I already have.
33. As a student, I want to have multiple skripsi projects (in case I switch topics), so that I don't lose my previous work.
34. As a student, I want the app in Bahasa Indonesia, so that I don't have to context-switch between English UI and Indonesian content.
35. As a student, I want automatic dark mode based on my system preference, so that I can write comfortably at night.

## Implementation Decisions

### Architecture
- **Monolith deployment**: single Cloud Run service running FastAPI + LibreOffice headless. Split into API + worker services only when export queue latency becomes a problem.
- **API-first**: Vue SPA communicates with FastAPI backend via REST endpoints. OpenAPI schema auto-generated by FastAPI.

### Data Model
- **PostgreSQL** (Cloud SQL) for all structured data: users, skripsi projects, sections (content as JSONB), pedoman presets, citations, konsultasi log entries, snapshots.
- **GCS** for uploaded PDF files, with references stored in the citations table.
- **One user → many projects, one project → one pedoman preset, one project → many sections/citations/konsultasi entries.**

### Pedoman System
- Structured form captures: page margins, paper size, font family + size (body/headings), line spacing, citation style (APA/IEEE/Vancouver/Chicago/Harvard), heading numbering format, page numbering rules, required sections/BABs with sub-sections, and min/max page counts per section.
- Presets are public and flaggable. Trust signal: "Digunakan oleh N mahasiswa." Seeded with 10 university presets at launch (UI, UGM, ITB, UNPAD, UNDIP, UB, UNAIR, UNS, UNHAS, BINUS).

### Citation Extraction Pipeline
1. Student uploads PDF → `pdf2doi` extracts DOI via regex/metadata
2. DOI found → CrossRef API → structured metadata
3. No DOI → `PyMuPDF` extracts first-page text → OpenAlex title search → fuzzy match
4. No match → Gemini attempts extraction from first-page text
5. Fallback → student pastes DOI or fills manual form
6. Store PDF in GCS + structured metadata in PostgreSQL
7. Format citation string per pedoman citation style

### Paper Search
- Data sources: OpenAlex (breadth, Indonesian journal coverage) + Semantic Scholar (AI summaries, recommendations).
- Three modes: keyword search, natural language query (Gemini reformulates into search terms), "find similar" (Semantic Scholar recommendations API).

### DOCX/PDF Export
- `python-docx` builds document structure programmatically from section content + pedoman formatting rules.
- LibreOffice headless post-processes: refreshes Table of Contents, resolves field codes for page numbering.
- PDF generated via `libreoffice --convert-to pdf` from the DOCX. One pipeline, not two.

### AI Features
- All AI calls go through Gemini API.
- Grammar/style: LanguageTool (self-hosted or API) for basic grammar, Gemini for academic style in Bahasa Indonesia.
- AI boundary enforced: suggest, summarize, paraphrase, search, validate — never generate skripsi content.
- Premium gate: 5 free AI actions/day, unlimited after one-time payment per project.

### Auth
- Google OAuth only. No email/password. No university SSO.

### Payments
- Midtrans integration. Supports QRIS, GoPay, OVO, bank transfer.
- One-time Rp 50.000 per skripsi project.

### Frontend
- Vue.js SPA. Tiptap (ProseMirror) rich text editor per section.
- Plus Jakarta Sans typography. Teal accent on neutral base. Dark mode via CSS custom properties + `prefers-color-scheme`.
- Landing page as a Vue route, no separate marketing site.

### Version History
- Auto-save snapshots per section (timestamped). Stored as JSONB diffs for storage efficiency.
- No git-like branching or commit messages.

## Testing Decisions

### Primary Seam: FastAPI HTTP Boundary
- All features tested through API endpoints. Tests call the same REST API that the Vue frontend calls.
- Test external behavior: "POST a PDF to /citations/upload → get back structured metadata" — not "pdf2doi correctly regex'd the DOI."
- Auth tested via mocked Google OAuth tokens.
- DOCX/PDF export tested by calling the export endpoint and validating the resulting file (check margins, fonts, TOC presence via python-docx inspection of the output).
- Pedoman CRUD, konsultasi log CRUD, section CRUD, snapshot retrieval — all through API.

### Secondary Seam: Extraction Pipeline
- The PDF → metadata chain is the most complex internal logic. Tested as a unit with stubbed external API calls (CrossRef, OpenAlex, Semantic Scholar, Gemini).
- Test cases: PDF with embedded DOI, PDF without DOI but findable via title, PDF not in any database (falls through to manual), scanned PDF with no text layer.
- External APIs stubbed with recorded responses to keep tests fast and deterministic.

### What Makes a Good Test
- Tests verify external behavior observable by the user, not implementation internals.
- A good test breaks when the feature breaks, not when the code is refactored.
- Each test covers one user-visible scenario. Name tests after the scenario, not the function.

## Out of Scope

- **Group skripsi / real-time collaboration**: solo-author only. Tiptap collaboration extension is the upgrade path if needed later.
- **Custom citation styles**: only APA, IEEE, Vancouver, Chicago, Harvard. CSL adoption if custom demand exceeds ~5% of users.
- **University SSO integration**: each uni has different systems or none. Google OAuth covers all students.
- **Mobile-optimized editor**: responsive web works for checking progress and konsultasi log on mobile, but the writing experience targets laptop/desktop.
- **Separate marketing/landing site**: Vue route is sufficient for launch.
- **Account sharing prevention**: at Rp 50.000 per project, not worth the engineering cost for v1.
- **Offline/PWA support**: online-only, optimize for low bandwidth instead.
- **Native mobile app**: not planned.

## Further Notes

- **Indonesian journal coverage gap**: ~10-20% of references from local Indonesian journals lack DOIs and won't appear in CrossRef/OpenAlex. Manual entry fallback is unavoidable and should be frictionless.
- **LibreOffice in Cloud Run**: container image will be larger (~500MB+). Acceptable for monolith; consider pre-built base image to speed up cold starts.
- **Pedoman cold start**: seed 10 university presets before launch. Accuracy matters — verify each against the actual published pedoman PDF.
- **LanguageTool Indonesian**: Indonesian support exists but is less mature than English. Gemini compensates for gaps in academic style checking.
- **Pricing validation**: Rp 50.000 is an assumption. Validate with 10-20 students before committing to the price point.
