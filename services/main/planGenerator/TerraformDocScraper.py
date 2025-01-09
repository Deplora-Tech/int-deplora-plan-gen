from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import markdownify
from core.logger import logger
from services.main.utils.caching.redis_service import TFDocsCache

class TerraformDocScraper:
    """
    Singleton class that manages a single Selenium browser instance and scrapes content.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TerraformDocScraper, cls).__new__(cls)
        return cls._instance

    async def initialize_browser(self):
        """
        Initialize the Selenium browser instance using WebDriverManager.
        """
        options = Options()
        options.add_argument('--headless=new')
        # options.add_argument('--disable-gpu')
        # options.add_argument('--no-sandbox')

        try:
            self.browser = webdriver.Chrome(service=ChromeDriverManager().install(), options=options)
            logger.info("Browser initialized.")
        except WebDriverException as e:
            logger.error("Failed to initialize the browser.")
            logger.error(str(e))
            self.browser = None

    async def fetch_definition(self, resource_name: str) -> str:
        """
        Fetch the Terraform resource definition from the Terraform Registry.
        """
        logger.info(f"Fetching definition for {resource_name}.")

        resource_name = resource_name.replace("aws_", "")

        # Check if the definition is already cached
        cached_definition = TFDocsCache.get_docs(resource_name)
        if cached_definition:
            logger.info(f"Definition found in cache for {resource_name}.")
            return cached_definition

        # Define the URL for the resource
        base_url = "https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/"
        resource_url = f"{base_url}{resource_name}"

        try:
            # Navigate to the resource URL
            self.browser.get(resource_url)

            # Wait for the content to load (implicit wait can be set globally)
            self.browser.implicitly_wait(10)

            # Extract the content inside the element with the id "provider-docs-content"
            try:
                element = self.browser.find_element(By.ID, "provider-docs-content")
                html = element.get_attribute("innerHTML")
                content = markdownify.markdownify(html, heading_style="ATX")

                if "This documentation page doesn't exist" in content:
                    content = None

            except NoSuchElementException:
                content = None

        except Exception as e:
            logger.error(f"An error occurred while fetching the definition for {resource_name}.")
            logger.error(str(e))
            content = None

        if content is None:
            logger.error(f"Definition not found for {resource_name}.")
        else:
            logger.info(f"Definition found for {resource_name}.")

        # Cache the definition
        TFDocsCache.store_docs(resource_name, content)

        return content

    def close_browser(self):
        """
        Close the browser instance.
        """
        if self.browser:
            self.browser.quit()
            logger.info("Browser closed.")
