from playwright.sync_api import Page, expect

class ClickHelper:
    """
    A utility class providing functionality to improve clicking reliability.
    """
    def __init__(self, page: Page):
        self.page = page

def click(locator_string, page=None)-> None:
    try:
        page.on("domcontentloaded")
        page.wait_for_load_state('load')
        page.wait_for_selector(locator_string)
        element = page.locator(locator_string)
        page.click(element)
    except Exception as locatorClickError:
                print(f"Failed to click element with error: {locatorClickError}, trying again...")
                element = page.locator(locator_string)
                page.click(element)






