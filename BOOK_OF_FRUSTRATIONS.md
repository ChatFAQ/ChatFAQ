# Book Of Frustrations

This file is intended for writing down all those TODOs/tech. deb. you know it needs to be addressed.

- [ ] Intent name and utterance generation is done with OpenAI, it should work with each LLM provider.
- [ ] Clusterization for intent generation doesn't work with ColBERT retriever yet.
- [ ] We should unify the back Dockerfiles into one.
- [ ] Modularize dependencies between cpu/gpu and other divisions.
- [ ] RAG need to be deleted and created if the retriever type wants to be changed. This deletion and creation shouldn't be needed and the RAG should be able to handle this change.
- [ ] Search correct faiss-gpu version and pin it.
- [ ] Default PDF parser doesn't handle images yet.
- [ ] Remove the cache system from the item store.
- [ ] Accept a list of ids to be deleted in the conversation API endpoint so the widget won't need to call the endpoint multiple times.
- [ ] The admin should make use of the directory routing so back button works better and links actually bring you to edit pages.
- [ ] Admin: Add the composables (as such useNuxtApp ($axios), useItemsStore, etc...) inside the utility functions on the admin (itemstore, utls, etc...) so we won't pass them as parameters.
- [ ] Admin: Axios should implement authetication with a middleware.
- [ ] Migrate fully from celery to ray by giving the ray workers access to the backend. 
