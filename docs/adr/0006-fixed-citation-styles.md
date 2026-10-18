# Pedoman ships with fixed citation styles, no custom engine

Citation formatting supports a fixed set of known styles: APA 7th, IEEE, Vancouver, Chicago, Harvard. No custom style definition engine.

**Why no custom styles:** Building a citation style engine (CSL-level) is a project in itself. These five styles cover 95%+ of Indonesian university pedomans. The remaining edge cases ("APA tapi tanpa DOI") are better handled by adding specific style variants based on user requests than by building a general-purpose formatter.

**Upgrade path:** If custom demand exceeds ~5% of users, adopt CSL (Citation Style Language) — an open XML-based standard with 10,000+ existing styles. Until then, hardcoded formatters per style are simpler and more reliable.
