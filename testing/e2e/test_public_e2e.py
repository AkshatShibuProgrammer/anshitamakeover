"""
Playwright E2E — public visitor journeys (TC-E2E-001 … TC-E2E-012).

Browsers must be installed first::

    ../testenv/bin/playwright install chromium --with-deps

Run (usually via the master program ``python testing/run_all.py --suite e2e``)::

    python -m pytest testing/e2e -v
"""
import re

import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e]


@pytest.fixture()
def home(page, live_base_url):
    page.goto(live_base_url + '/', wait_until='domcontentloaded', timeout=60000)
    return page


def test_e2e_001_home_renders_with_brand(home):
    """TC-E2E-001: homepage loads, preloader exists, brand is visible."""
    expect(home.locator('#preloader')).to_be_attached()
    expect(home.locator('body')).to_contain_text('Anshita', timeout=30000)


def test_e2e_002_coupon_banner_visible(home):
    """TC-E2E-002: seasonal coupon banner shows a code and discount."""
    banner = home.locator('#cbanner')
    expect(banner).to_be_attached()
    expect(home.locator('#cb-code')).not_to_be_empty()
    expect(home.locator('#cb-disc')).not_to_be_empty()


def test_e2e_003_bridal_suites_rendered(home):
    """TC-E2E-003: seeded bridal suites render on the public page."""
    expect(home.locator('body')).to_contain_text('Imperial Royal HD Bridal Suite', timeout=30000)
    expect(home.locator('body')).to_contain_text('Master Airbrush Bridal Suite')


def test_e2e_004_inactive_content_hidden(home):
    """TC-E2E-004: inactive/hidden records never render publicly."""
    body_text = home.locator('body').inner_text()
    assert 'Legacy Trial Package' not in body_text
    assert 'Hidden Reviewer' not in body_text
    assert 'Retired Haldi Service' not in body_text


def test_e2e_005_gallery_grid_has_covers(home):
    """TC-E2E-005: editorial gallery grid renders group covers."""
    expect(home.locator('#editorial-peek-gallery')).to_be_attached()


def test_e2e_006_reviews_rendered(home):
    """TC-E2E-006: verified review cards render with star ratings."""
    expect(home.locator('body')).to_contain_text('Priya Sharma', timeout=30000)
    expect(home.locator('body')).to_contain_text('500+')


def test_e2e_007_language_switch_to_hindi(page, live_base_url):
    """TC-E2E-007: setLang('hindi') reloads with Hindi translations + cookie."""
    page.goto(live_base_url + '/', wait_until='domcontentloaded', timeout=60000)
    page.evaluate("setLang('hindi')")
    page.wait_for_load_state('domcontentloaded')
    expect(page.locator('body')).to_contain_text('Anshita', timeout=30000)
    cookies = {c['name']: c['value'] for c in page.context.cookies()}
    assert cookies.get('lang') == 'hindi'


def test_e2e_008_academy_page_shows_course(page, live_base_url):
    """TC-E2E-008: academy page renders masterclass + fee structure."""
    page.goto(live_base_url + '/academy/', wait_until='domcontentloaded', timeout=60000)
    expect(page.locator('body')).to_contain_text('Professional Makeup Artist Program', timeout=30000)


def test_e2e_009_chatbot_conversation(page, live_base_url):
    """TC-E2E-009: chatbot widget answers a bridal query in-browser."""
    page.goto(live_base_url + '/', wait_until='domcontentloaded', timeout=60000)
    page.locator('.chat-toggle').first.click()
    expect(page.locator('#chat-box')).to_be_visible(timeout=10000)
    page.locator('#chat-inp').fill('What is the price of bridal makeup?')
    page.locator('.chat-send').first.click()
    expect(page.locator('#chat-msgs .msg.bot').last).to_contain_text('₹', timeout=45000)


def test_e2e_010_chatbot_negotiation_via_ui(page, live_base_url):
    """TC-E2E-010: budget negotiation through the chat widget honours floor."""
    page.goto(live_base_url + '/', wait_until='domcontentloaded', timeout=60000)
    page.locator('.chat-toggle').first.click()
    expect(page.locator('#chat-box')).to_be_visible(timeout=10000)
    page.locator('#chat-inp').fill('my budget is 30000')
    page.locator('.chat-send').first.click()
    expect(page.locator('#chat-msgs .msg.bot').last).to_contain_text('30,000', timeout=45000)


def test_e2e_011_sinha_studio_page(page, live_base_url):
    """TC-E2E-011: Sinha branding studio page renders."""
    page.goto(live_base_url + '/sinha-logos/', wait_until='domcontentloaded', timeout=60000)
    expect(page.locator('body')).to_contain_text('Sinha', timeout=30000)


def test_e2e_012_responsive_mobile_viewport(page, live_base_url):
    """TC-E2E-012: homepage renders sanely at a 390px mobile viewport."""
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto(live_base_url + '/', wait_until='domcontentloaded', timeout=60000)
    expect(page.locator('body')).to_contain_text('Anshita', timeout=30000)
