# DOCX export via python-docx + LibreOffice headless

Final DOCX export uses python-docx to build the document structure and LibreOffice headless to post-process (refresh TOC, fix page numbering, resolve field codes).

**Why not python-docx alone:** python-docx cannot generate a live Table of Contents or handle complex page numbering schemes (Roman numerals for front matter, Arabic for body) that Indonesian pedomans universally require. These features depend on Word field codes that only a Word-compatible engine can resolve.

**Why not Pandoc:** Pandoc's DOCX output offers less fine-grained control over margins, heading styles, and page numbering per-section than building the document programmatically with python-docx.

**Deployment:** LibreOffice runs headless in the same Cloud Run container. Export is async — student clicks export, job queues, DOCX ready for download in seconds.
