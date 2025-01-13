from selenium import webdriver
from selenium.webdriver.common.by import By
import markdownify
from selenium.common.exceptions import WebDriverException
from core.logger import logger
from services.main.utils.caching.redis_service import TFDocsCache
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


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

        try:
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")

            # self.browser = webdriver.Chrome(options=options)
            self.browser_options = options
            logger.info("Browser initialized.")
        except WebDriverException as e:
            logger.error("Failed to initialize the browser.")
            logger.error(str(e))
            self.browser_options = None
        except Exception as e:
            logger.error("An error occurred while initializing the browser.")
            logger.error(str(e))
            self.browser_options = None

    def fetch_definition(self, resource_name: str) -> str:
        """
        Fetch the Terraform resource definition from the Terraform Registry.
        """
        logger.info(f"Fetching definition for {resource_name}.")
        
        

        ignored_errors = [NoSuchElementException, ElementNotInteractableException]

        resource_name = resource_name.replace("aws_", "").replace("azurerm_", "").replace("google_", "")

        # Check if the definition is already cached
        cached_definition = TFDocsCache.get_docs(resource_name)
        if cached_definition:
            logger.info(f"Definition found in cache for {resource_name}.")
            return cached_definition

        # Define the URL for the resource
        base_url = "https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/"
        resource_url = f"{base_url}{resource_name}"

        try:
            browser = webdriver.Chrome(options=self.browser_options)
            # Navigate to the resource URL
            browser.get(resource_url)

            wait = WebDriverWait(
                browser,
                timeout=10,
                poll_frequency=0.2,
                ignored_exceptions=ignored_errors,
            )
            element = wait.until(
                EC.visibility_of_element_located((By.ID, "provider-docs-content"))
            )
            html = element.get_attribute("innerHTML")
            content = markdownify.markdownify(html, heading_style="ATX")

            if "This documentation page doesn't exist" in content:
                content = None

        except Exception as e:
            logger.error(
                f"An error occurred while fetching the definition for {resource_name}."
            )
            logger.error(str(e))
            content = None
        
        finally:
            browser.quit()

        if content is None:
            logger.error(f"Definition not found for {resource_name}.")
        else:
            logger.info(f"Definition found for {resource_name}.")

        # Cache the definition
        TFDocsCache.store_docs(resource_name, content)

        return content
