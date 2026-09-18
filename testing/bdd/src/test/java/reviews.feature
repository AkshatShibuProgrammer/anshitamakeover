Feature: Customer reviews — submit & moderate (TC-KRT-REV)

Background:
  * url baseUrl

Scenario: TC-KRT-REV-001 submission requires a name
  Given path '/api/review/submit/'
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And request { review_text: 'missing name probe' }
  When method post
  Then status 200
  And match response.ok == false

Scenario: TC-KRT-REV-002 valid submission persists then admin deletes it
  * def clientName = 'Karate Reviewer ' + java.util.UUID.randomUUID().toString().substring(0,8)
  Given path '/api/review/submit/'
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And request { client_name: '#(clientName)', review_text: 'Karate probe review', rating: 5 }
  When method post
  Then status 200
  And match response.ok == true
  * def reviewId = response.review_id

  Given path '/api/admin/review/'
  And cookie sessionid = sessionCookie
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-portal/'
  And request { action: 'delete', id: '#(reviewId)' }
  When method post
  Then match response.ok == true

Scenario: TC-KRT-REV-003 rating clamps into 1..5 and row is cleaned up
  * def clientName = 'Karate Overrater ' + java.util.UUID.randomUUID().toString().substring(0,8)
  Given path '/api/review/submit/'
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And request { client_name: '#(clientName)', review_text: 'clamp probe', rating: 99 }
  When method post
  Then status 200
  And match response.ok == true
  * def reviewId = response.review_id

  Given path '/api/admin/review/'
  And cookie sessionid = sessionCookie
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-portal/'
  And request { action: 'delete', id: '#(reviewId)' }
  When method post
  Then match response.ok == true

Scenario: TC-KRT-REV-004 admin review list requires staff session
  Given path '/api/admin/review/'
  When method get
  Then status 302
  And match header Location contains '/admin-login/'
