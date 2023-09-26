from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler, BrowserContextWrapper, \
    PERSISTENT_CONTEXT_PATH_KEY, DEFAULT_CONTEXT_NAME, _attach_page_event_handlers
from logging import getLogger
from undetected_playwright import stealth_async

import asyncio
from typing import Optional

from playwright.async_api import Page
from scrapy import Spider
from scrapy.http import Request, Response

logger = getLogger(__name__)


class ScrapyCustomPlaywrightDownloadHandler(ScrapyPlaywrightDownloadHandler):

    async def _create_browser_context(
        self,
        name: str,
        context_kwargs: Optional[dict],
        spider: Optional[Spider] = None,
    ) -> BrowserContextWrapper:
        """Create a new context, also launching a browser if necessary."""
        if hasattr(self, "context_semaphore"):
            await self.context_semaphore.acquire()
        context_kwargs = context_kwargs or {}
        if context_kwargs.get(PERSISTENT_CONTEXT_PATH_KEY):
            context = await self.browser_type.launch_persistent_context(**context_kwargs)
            await stealth_async(context)
            persistent = True
            self.stats.inc_value("playwright/context_count/persistent")
        else:
            await self._maybe_launch_browser()
            context = await self.browser.new_context(**context_kwargs)
            await stealth_async(context)
            persistent = False
            self.stats.inc_value("playwright/context_count/non_persistent")
        context.on("close", self._make_close_browser_context_callback(name, persistent, spider))
        logger.debug(
            "Browser context started: '%s' (persistent=%s)",
            name,
            persistent,
            extra={"spider": spider, "context_name": name, "persistent": persistent},
        )
        self.stats.inc_value("playwright/context_count")
        if self.default_navigation_timeout is not None:
            context.set_default_navigation_timeout(self.default_navigation_timeout)
        self.context_wrappers[name] = BrowserContextWrapper(
            context=context,
            semaphore=asyncio.Semaphore(value=self.max_pages_per_context),
            persistent=persistent,
        )
        self._set_max_concurrent_context_count()
        return self.context_wrappers[name]

    async def _download_request(self, request: Request, spider: Spider) -> Response:
        page = request.meta.get("playwright_page")
        if not isinstance(page, Page):
            page = await self._create_page(request=request, spider=spider)
        context_name = request.meta.setdefault("playwright_context", DEFAULT_CONTEXT_NAME)

        _attach_page_event_handlers(
            page=page, request=request, spider=spider, context_name=context_name
        )

        # For some reason routing make the downloads to fail with a: certificate failed error
        """
        await page.unroute("**")
        await page.route(
            "**",
            self._make_request_handler(
                context_name=context_name,
                method=request.method,
                url=request.url,
                headers=request.headers,
                body=request.body,
                encoding=request.encoding,
                spider=spider,
            ),
        )
        """

        try:
            result = await self._download_request_with_page(request, page, spider)
        except Exception as ex:
            if not request.meta.get("playwright_include_page") and not page.is_closed():
                logger.warning(
                    "Closing page due to failed request: %s exc_type=%s exc_msg=%s",
                    request,
                    type(ex),
                    str(ex),
                    extra={
                        "spider": spider,
                        "context_name": context_name,
                        "scrapy_request_url": request.url,
                        "scrapy_request_method": request.method,
                        "exception": ex,
                    },
                )
                await page.close()
                self.stats.inc_value("playwright/page_count/closed")
            raise
        else:
            return result
