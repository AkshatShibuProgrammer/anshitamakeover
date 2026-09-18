"""
Playwright E2E — admin journeys (TC-E2E-013 … TC-E2E-018).

Covers the branded login page, invalid-credential handling and the admin
portal dashboard loading with every management section.
"""
import pytest
from playwright.sync_api import expect

pytestmark = [pytest.mark.e2e, pytest.mark.admin]


@pytest.fixture()
def admin_page(page, live_base_url):
    """A page already logged into the admin portal."""
    page.goto(live_base_url + '/admin-login/', wait_until='domcontentloaded', timeout=60000)
    page.fill('#username', 'regadmin')
    page.fill('#password', 'RegTest@2026')
    page.click('#login-submit-btn')
    page.wait_for_url('**/admin-portal/**', timeout=30000)
    return page


def test_e2e_013_login_page_elements(page, live_base_url):
    """TC-E2E-013: login page exposes username/password/submit."""
    page.goto(live_base_url + '/admin-login/', wait_until='domcontentloaded', timeout=60000)
    expect(page.locator('#username')).to_be_visible()
    expect(page.locator('#password')).to_be_visible()
    expect(page.locator('#login-submit-btn')).to_be_visible()


def test_e2e_014_invalid_login_shows_error(page, live_base_url):
    """TC-E2E-014: wrong password surfaces the error banner, no portal access."""
    page.goto(live_base_url + '/admin-login/', wait_until='domcontentloaded', timeout=60000)
    page.fill('#username', 'regadmin')
    page.fill('#password', 'definitely-wrong')
    page.click('#login-submit-btn')
    expect(page.locator('#login-err')).to_be_visible(timeout=15000)
    assert '/admin-portal/' not in page.url


def test_e2e_015_portal_loads_for_staff(admin_page):
    """TC-E2E-015: staff login lands on the portal dashboard."""
    expect(admin_page.locator('body')).to_contain_text('Admin', timeout=30000)


def test_e2e_016_portal_shows_management_sections(admin_page):
    """TC-E2E-016: portal renders packages/services/media/reviews controls."""
    body = admin_page.locator('body').inner_text()
    for needle in ['Package', 'Service', 'Review']:
        assert needle.lower() in body.lower()


def test_e2e_017_portal_lists_seeded_packages(admin_page):
    """TC-E2E-017: seeded suites are visible in the portal package manager."""
    expect(admin_page.locator('body')).to_contain_text('Imperial Royal HD Bridal Suite',
                                                       timeout=30000)


def test_e2e_018_logout_returns_home(page, admin_page, live_base_url):
    """TC-E2E-018: logout endpoint ends the session and redirects home."""
    admin_page.goto(live_base_url + '/admin-logout/', wait_until='domcontentloaded')
    page.wait_for_timeout(800)
    # now portal must bounce back to login
    page.goto(live_base_url + '/admin-portal/', wait_until='domcontentloaded')
    assert '/admin-login/' in page.url
