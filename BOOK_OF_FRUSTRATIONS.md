# Book Of Frustrations

This file is intended for writing down all those TODOs/tech. deb. you know it needs to be addressed.

- [ ] We should unify the back Dockerfiles into one.
- [ ] Modularize dependencies between cpu/gpu and other divisions.
- [ ] Search correct faiss-gpu version and pin it.
- [ ] Default PDF parser doesn't handle images yet.
- [ ] Accept a list of ids to be deleted in the conversation API endpoint so the widget won't need to call the endpoint multiple times.
- [ ] The admin should make use of the directory routing so back button works better and links actually bring you to edit pages.
- [ ] Admin: Add the composable (as such useNuxtApp ($axios), useItemsStore, etc...) inside the utility functions on the admin (itemstore, utls, etc...) so we won't pass them as parameters.
- [ ] Admin: Axios should implement authentication with a middleware.
- [ ] Redo the stats after the RAG removal.
- [ ] Widget: If the widget won't show the list of conversations due to a render attribute that hides them, then it shouldn't be requesting them.
- [ ] SDK: Typify the MML from the context, so it has its own secured method to access the different data structure inside MMLs as such 'content', 'knowledge_items', etc...
- [ ] Widget: On the preview mode dummy messages we should be adding markup links and prefilled user feedback in other to have a more complete preview.
- [ ] SDK: Currently the FSM definition can have contradictions, we should add a validation method to check for them. ex: you can declare transition between states and not provide the state itself.
- [ ] SDK/Backend: When creating a data source parser the data source information that comes from the backend should have all the information of the different data source types (nowdays only the url comes with it) ex: in csv data source type the index columns, if it has headers or not, etc... also a metadata field inside the backend datasource would be nice to have, so we can pass this metadata to the custom parsers and make everything more dynamic.
- [ ] Backend: We should rename env var BACKEND_TOKEN to CHATFAQ_TOKEN just for consistency purposes
- [ ] Backend: Prompt Config should have a FK to the Knowledge Base for authentification purposes.

## Deferred `chat-rag` dependency upgrades

The following upgrades were identified while preparing `chat-rag 0.2.15` but
were deliberately excluded from that release. The regenerated lock file
already contains the newest versions allowed by the current constraints.
Moving beyond them requires widening constraints and validating behavioral or
API changes. Versions below were observed on 2026-11-19.

### Blocked PDF/HTML parsing

- [ ] Restore PDF and HTML parsing on Python 3.14. The parser depends on
      `unstructured` and `unstructured-inference`, which currently require
      Python `<3.14`. This is not a regression introduced by `chat-rag 0.2.15`:
      the previous manifest constrained `unstructured` to Python `<3.12` while
      `chat-rag 0.2.14` targeted Python 3.13, so parsing was already
      unavailable. Replace the parser or wait for upstream Python 3.14 support,
      then restore the dependencies and add end-to-end PDF/HTML ingestion
      coverage.

### High-risk API migrations

These upgrades cross major or otherwise significant API boundaries. They
should be handled separately and backed by focused tests for every affected
integration.

| Package | Locked | Available | Main concern |
| --- | ---: | ---: | --- |
| `accelerate` | 0.31.0 | 1.16.0 | Major ML runtime and configuration changes |
| `anthropic` | 0.68.2 | 2.10.0 | Client, request, streaming, and response API changes |
| `bm25s` | 0.1.10 | 0.3.16 | Pre-1.0 retrieval API and index compatibility |
| `google-genai` | 1.75.0 | 3.6.1 | Major client and content-model changes |
| `mistralai` | 1.12.4 | 3.8.0 | Major client and response-model changes |
| `openai` | 1.109.1 | 3.55.1 | Major client, streaming, tools, and response API changes |
| `pandas` | 2.3.3 | 3.1.1 | Removed APIs and changed data-processing behavior |
| `sentence-transformers` | 2.7.0 | 6.3.0 | Multiple major model and encoding API changes |
| `together` | 1.5.35 | 3.3.0 | Major SDK migration; the installed 1.x SDK is deprecated |
| `transformers` | 4.57.6 | 5.23.0 | Major model-loading and generation changes |

### More isolated upgrades that still need validation

These are less coupled to ChatFAQ behavior, but their constraint changes and
runtime compatibility should still be tested instead of being folded into an
unrelated Python upgrade.

| Package | Locked | Available | Validation needed |
| --- | ---: | ---: | --- |
| `certifi` | 2025.11.12 | 2026.10.23 | TLS/network smoke tests |
| `docstring-parser` | 0.16 | 0.18.0 | Structured-output and tool-schema generation |
| `einops` | 0.6.1 | 0.8.2 | Embedding-model tensor transformations |
| `pillow` | 11.3.0 | 13.0.0 | Image and multimodal input handling |
| `pyarrow` | 22.0.0 | 26.0.1 | Dataset serialization and interchange |
| `python-dotenv` | 0.21.1 | 1.2.4 | Environment-loading behavior |
| `umap-learn` | 0.5.12 | 0.6.0 | Clustering and dimensionality reduction |

### Coordinated backend/GPU upgrade

- [ ] Upgrade `torch` from 2.10.0 to 2.15.0 only together with the backend GPU
      image and its pinned CUDA/CPython wheel. Validate CPU imports, GPU image
      construction, CUDA compatibility, embeddings, and retrieval before
      changing the package constraint.

### Upgrade strategy

- [ ] Add meaningful automated coverage for the LLM clients, embeddings,
      retrievers, and clustering paths before widening the high-risk
      constraints.
- [ ] Upgrade provider SDKs independently so failures can be attributed to one
      integration.
- [ ] Keep the ML stack aligned across `chat-rag`, backend images, Ray workers,
      and GPU deployment images.
