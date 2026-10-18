# Vue SPA with Tiptap rich-text editor

Frontend uses Vue.js as SPA framework with Tiptap (ProseMirror-based) for the per-section rich text editing experience.

**Why Vue over React:** Solo developer project — Vue's simpler mental model and single-file components reduce friction. Tiptap has first-class Vue bindings. Ecosystem covers all needs (component libraries, state management, routing).

**Why Tiptap over Quill/TinyMCE/CKEditor:** Open-source, ProseMirror under the hood (battle-tested), extensible for custom toolbar actions (paraphrase selection, insert citation, AI suggestions). If group skripsi collaboration is needed later, Tiptap has a collaboration extension (Yjs-based CRDT) — upgrade path exists without switching editors.

**Considered alternatives:**
- React: rejected for solo-dev complexity overhead
- Svelte: rejected because Tiptap Vue integration is more mature
- HTMX: rejected because the editing experience needs client-side richness
- Quill: rejected for limited extensibility
