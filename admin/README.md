The /ChatFAQ/admin folder contains the code for the ChatFAQ admin interface.

Specifically:

- It is a Nuxt.js application that provides a dashboard/GUI for administrating ChatFAQ functionality like managing bots, conversations, users etc.

- The folder contains the Nuxt.js project files like components, pages, plugins etc that make up the admin interface.

- It has other subfolders that contain assets, static files, and test files for the Nuxt admin app.

As seen in the Dogfile configuration, ChatFAQ deploys the admin interface as a separate container/service called "admin".

The "admin" service builds an image using the code inside this /admin folder, and configures it to run alongside the other ChatFAQ services.

So in summary, the /admin folder houses the source code for the Nuxt.js based admin dashboard application. This provides a GUI for admins to manage ChatFAQ, and gets deployed as part of the overall ChatFAQ platform stack.

# Nuxt 3 Minimal Starter

Look at the [Nuxt 3 documentation](https://nuxt.com/docs/getting-started/introduction) to learn more.

## Setup

Make sure to install the dependencies:

```bash
# npm
npm install

# pnpm
pnpm install

# yarn
yarn install

# bun
bun install
```

## Development Server

Start the development server on `http://localhost:3000`:

```bash
# npm
npm run dev

# pnpm
pnpm run dev

# yarn
yarn dev

# bun
bun run dev
```

## Production

Build the application for production:

```bash
# npm
npm run build

# pnpm
pnpm run build

# yarn
yarn build

# bun
bun run build
```

Locally preview production build:

```bash
# npm
npm run preview

# pnpm
pnpm run preview

# yarn
yarn preview

# bun
bun run preview
```

Check out the [deployment documentation](https://nuxt.com/docs/getting-started/deployment) for more information.
