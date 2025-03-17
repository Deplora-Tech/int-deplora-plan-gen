from playwright.async_api import async_playwright
from markdownify import markdownify
from core.logger import logger
from services.main.utils.caching.redis_service import TFDocsCache
from playwright.async_api import TimeoutError as PlaywrightTimeoutError
import traceback

class TerraformDocScraper:
    """
    Singleton class that manages a Playwright browser instance and scrapes content.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TerraformDocScraper, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.browser = None

    async def initialize_browser(self):
        """
        Initialize the Playwright browser instance.
        """
        if not self.browser:
            logger.info("Initializing Playwright browser...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            logger.info("Playwright browser initialized.")

    async def fetch_definition(self, resource_name: str) -> str:
        """
        Fetch the Terraform resource definition from the Terraform Registry.
        """
        content = None

        try:
            logger.info(f"Fetching definition for {resource_name}.")

            # Check if the definition is already cached
            cached_definition = TFDocsCache.get_docs(resource_name)
            if cached_definition:
                logger.info(f"Definition found in cache for {resource_name}.")
                return cached_definition
            else:
                logger.info(f"Definition not found in cache for {resource_name}.")

            # Define the URL for the resource
            base_url = "https://registry.terraform.io/providers/hashicorp/"
            provider, resource = resource_name.split('_', 1)
            resource_url = f"{base_url}{provider}/latest/docs/resources/{resource}"

            if self.browser:
                await self.browser.close()
                self.browser = None
            
            if not self.browser:
                await self.initialize_browser()
            else:
                logger.info("Reusing existing Playwright browser instance.")

            context = await self.browser.new_context()
            logger.info(f"New Playwright context created for {resource_name}.")
            page = await context.new_page()
            logger.info(f"Loading page for {resource_name}...")
            await page.goto(resource_url, timeout=10000)
            logger.info(f"Page loaded for {resource_name}.")
            try:
                # Wait for the element containing the content to be visible
                element = await page.wait_for_selector("#provider-docs-content", timeout=10000)
                html = await element.inner_html()
                content = markdownify(html, heading_style="ATX")

                if "This documentation page doesn't exist" in content:
                    content = None

            except PlaywrightTimeoutError:
                logger.error(f"Timeout while waiting for content on {resource_url}.")

            await page.close()

        except Exception as e:
            logger.error(f"An error occurred while fetching the definition for {resource_name}.")
            logger.error(traceback.format_exc())

        if content is None:
            logger.error(f"Definition not found for {resource_name}.")
        else:
            logger.info(f"Definition found for {resource_name}.")
            # Cache the definition
            TFDocsCache.store_docs(resource_name, content)

        return content
