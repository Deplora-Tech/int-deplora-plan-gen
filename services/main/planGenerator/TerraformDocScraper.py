from playwright.async_api import async_playwright
import markdownify
from core.logger import logger

class TerraformDocScraper :
    """
    Singleton class that manages a single Playwright browser instance and scrapes content.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TerraformDocScraper, cls).__new__(cls)
        return cls._instance

    async def initialize_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=True)
        logger.info("Browser initialized.")

    async def fetch_definition(self, resource_name: str) -> str:
        """
        Fetch the Terraform resource definition from the Terraform Registry.
        """
        logger.info(f"Fetching definition for {resource_name}.")
        base_url = "https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/"
        resource_url = f"{base_url}{resource_name}"

        page = await self.browser.new_page()

        try:
            # Navigate to the resource URL
            await page.goto(resource_url)

            # Wait for the content to load
            await page.wait_for_selector("#provider-docs-content")

            # Extract the content inside the article tag
            element = await page.query_selector("#provider-docs-content")
            
            if not element:
                content = None
            
            else:
                html = await element.inner_html()
                content = markdownify.markdownify(html, heading_style="ATX")
                
                if "This documentation page doesn't exist" in content:
                    content = None
        
        except Exception as e:
            logger.error(f"An error occurred while fetching the definition for {resource_name}.")
            logger.error(str(e))
            content = None
            
        finally:
            # Close the page after scraping
            await page.close()
            
        if content is None:
            logger.error(f"Definition not found for {resource_name}.")
        else:
            logger.info(f"Definition found for {resource_name}.")

        return content

    def close_browser(self):
        """
        Close the browser instance and stop Playwright.
        """
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
