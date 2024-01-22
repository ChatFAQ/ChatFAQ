The admin/store directory contains Vuex store files used by the admin application.

Vuex is the official state management pattern+library for Vue.js applications. It serves a similar purpose to React's Redux.

The files:

- auth.js
  - Manages auth state like login status, user profile
- items.js
  - Could handle other global app state

Key points:

- Stores app state centrally for components
- auth.js handles authentication flow
- Other files can manage other entities
- Allows consuming components to read/modify state
- Better state management than passing props

How it works:

- Components import/use stores
- Stores export mutations, getters, actions
- Components dispatch actions, read state via getters

This centralizes state management in a predictable way per Vuex best practices.

The stores provide a single source of truth for authentication and other data needed across the admin app.

