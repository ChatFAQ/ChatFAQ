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
