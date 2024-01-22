The admin/server directory contains code related to running the admin application on the [server/backend](https://app.mutable.ai/beatricebustos/ChatFAQ#:~:text=application%20on%20the-,server,-/backend%20rather%20than) rather than the [client/frontend](https://app.mutable.ai/beatricebustos/ChatFAQ#:~:text=than%20the%20client/-,frontend,-.).

Some common uses of a server-side folder:

- API route definitions (if API is colocated)
- Server-side rendering configuration
- TypeScript configuration (tsconfig.json)
- Backend models/services
- Authentication/authorization
- Database/storage integration

Specifically, the tsconfig.json file in this directory:

- Configures TypeScript compilation settings for server code
- Defines compiler options like module, target, lib, declaration
- Helps maintain type safety across server codebase

So in summary:

- Location for server-side app code
- Separated from client-side code structure
- tsconfig.json sets TypeScript configuration
- Used if server API code is colocated

This structure distinguishes server vs client concerns and configuration, while still keeping them together in the monorepo.

