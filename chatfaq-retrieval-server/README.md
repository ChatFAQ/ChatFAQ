# API

This handles the API and back-office admin.

All the URLs pointing to this are prefixed by `/back`.


## Components

You'll find the following apps:

-   [people](./chatfaq_retrieval_server/apps/people) &mdash; The user model and
    authentication.


-   [realtime](./chatfaq_retrieval_server/apps/realtime) &mdash; Deals with
    websockets



## OpenAPI

When the app is in development mode, you can access the OpenAPI documentation at
`/back/api/schema/redoc/`.

This documentation is auto-generated using
[drf-spectacular](https://drf-spectacular.readthedocs.io/en/latest/). As you
create more APIs, make sure that they render nicely in OpenAPI format.
