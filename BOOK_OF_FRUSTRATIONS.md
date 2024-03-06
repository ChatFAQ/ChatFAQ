# Book Of Frustrations

This file is intended for writing down all those TODOs/tech. deb. you know it needs to be addressed.

- [ ] We should support filesystem storage as default storage.
- [ ] Intent name and utterance generation is done with OpenAI, it should work with each LLM provider.
- [ ] Clusterization for intent generation doesn't work with ColBERT retriever yet.
- [ ] We should unify the back Dockerfiles into one.
- [ ] Modularize dependencies between cpu/gpu and other divisions.
- [ ] RAGs should not be loaded in shared celery memory, but in another service which celery calls.
- [ ] RAG need to be deleted and created if the retriever type wants to be changed. This deletion and creation shouldn't be needed and the RAG should be able to handle this change.
- [ ] Search correct faiss-gpu version and pin it.
- [ ] Default PDF parser doesn't handle images yet.
- [ ] Remove the cache system from the item store.
