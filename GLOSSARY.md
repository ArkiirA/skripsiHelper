# SkripsiHelper

A thesis-writing tool for Indonesian university students. Guides them from blank page to defensible draft with structure, citation management, and advisor-revision tracking, formatted per their university's pedoman penulisan.

## Language

**Skripsi**:
An undergraduate thesis required for graduation at Indonesian universities.
_Avoid_: thesis (too generic), paper, tugas akhir (different at some unis)

**Pedoman**:
A university's official formatting and style guidelines for skripsi (margins, fonts, citation style, heading structure, page numbering).
_Avoid_: template, format guide, style guide

**Preset**:
A saved, reusable pedoman configuration for a specific university, created by a student and available to all students at that university.
_Avoid_: template, profile

**Daftar Pustaka**:
The bibliography/reference list in a skripsi, formatted per the university's pedoman.
_Avoid_: bibliography, references, works cited

**Konsultasi Log**:
A chronological record of advisor feedback from bimbingan sessions, with items marked resolved or unresolved.
_Avoid_: revision tracker, comment thread, feedback log

**Dosen Pembimbing**:
The thesis advisor. Not a user of the system — their feedback is entered by the student.
_Avoid_: advisor, supervisor, mentor

**Pencarian Paper**:
AI-assisted academic paper discovery. Student describes a topic or research question, system queries external databases and returns relevant papers with metadata.
_Avoid_: literature search, paper finder

**Extraction Pipeline**:
The chain that turns an uploaded PDF into structured citation metadata: DOI regex → CrossRef → text extraction → OpenAlex → AI fallback → manual entry.
_Avoid_: citation parser, reference extractor

**Snapshot**:
A timestamped auto-saved version of a section's content. Enables "go back to last week's version" without full git complexity.
_Avoid_: version, commit, revision

**Sidang**:
The formal thesis defense where a student presents and defends their skripsi before a panel of examiners.
_Avoid_: defense, viva, presentation

**Ekspor**:
The act of generating a final formatted document (DOCX or PDF) from the student's skripsi content, formatted per their university's pedoman.
_Avoid_: download, render, publish

## Design Language

**Warm & Approachable**:
The visual design direction — neutral base, soft edges, friendly tone. Lowers anxiety for stressed students facing deadlines.
_Avoid_: clinical, corporate, academic-portal aesthetic

**Teal Accent**:
The single accent color used for CTAs, progress indicators, and navigation across light and dark themes.
_Avoid_: multi-color schemes, brand rainbow
