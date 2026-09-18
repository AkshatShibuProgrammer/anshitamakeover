@ignore
Feature: Reusable admin login — returns sessionid cookie + fresh csrf token

Background:
  * url baseUrl

Scenario:
  # Warm up to get a csrftoken cookie (login page renders a CSRF form)
  Given path '/admin-login/'
  When method get
  Then status 200
  * def csrfToken = responseCookies['csrftoken'] ? responseCookies['csrftoken'].value : ''

  # Submit credentials
  Given path '/admin-login/'
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-login/'
  And form field username = adminUser
  And form field password = adminPass
  When method post
  Then status 302
  * def sessionCookie = responseCookies['sessionid'] ? responseCookies['sessionid'].value : ''
  # Re-warm csrf token bound to the authenticated session
  * def csrfToken = responseCookies['csrftoken'] ? responseCookies['csrftoken'].value : csrfToken
