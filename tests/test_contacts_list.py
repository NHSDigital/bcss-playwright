import logging
import random
import re
from os import environ

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

from pages.bcss_home_page import BcssHomePage
from pages.contacts_list import ContactsList
from pages.login import BcssLoginPage

load_dotenv()
logger = logging.getLogger(__name__)
expect.set_options(timeout=20_000)


@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page) -> None:
    username = environ.get("BCSS_USERNAME")
    password = environ.get("BCSS_PASSWORD")
    login_page = BcssLoginPage(page)
    login_page.login(username, password)


def get_to_screen(page: Page) -> None:
    homepage = BcssHomePage(page)
    expect(page.get_by_role("link", name="Screening Practitioner Appointments")).to_be_visible()
    homepage.click_contacts_list()
    page.screenshot(path="test-results/contacts_list/select_org_screen.png")
    expect(page.get_by_text("Contacts List")).to_be_visible()


def test_view_contacts(page: Page) -> None:
    get_to_screen(page)
    contacts_list = ContactsList(page)
    contacts_list.click_view_contacts()
    page.screenshot(path="test-results/contacts_list/contacts_list.png")
    expect(page.get_by_text("View Contacts")).to_be_visible()


def test_edit_my_contact_details(page: Page) -> None:
    get_to_screen(page)
    contacts_list = ContactsList(page)
    contacts_list.click_edit_my_contact_details()
    expect(page.get_by_text("Edit My Contact Details")).to_be_visible()
    expect(page.get_by_text("Telephone")).to_be_visible()
    test_number = generate_phone_number()
    page.locator("[name='A_C_TELEPHONE_NUMBER']").fill(test_number)
    page.get_by_text("Save").click()
    expect(page.get_by_text(test_number)).to_be_visible()
    page.screenshot(path="test-results/contacts_list/updated_number_save_clicked.png")
    expect(page.get_by_text("The action was performed successfully")).to_be_visible()


def generate_phone_number() -> str:
    # Generate 2 digits for first part
    first_part = "".join(str(random.randint(0, 9)) for _ in range(2))
    # Generate 2 digits for second part
    second_part = "".join(str(random.randint(0, 9)) for _ in range(2))
    # Generate 4 digits for third part
    third_part = "".join(str(random.randint(0, 9)) for _ in range(4))

    # Join them together to make the number and assert its correct and return it
    phone_number = f"{first_part} {second_part} {third_part}"
    assert re.fullmatch(
        r"\d{2}\s\d{2}\s\d{4}", phone_number
    ), f"Phone number '{phone_number}' does not match expected format 'XX XX XXXX'"

    return phone_number
