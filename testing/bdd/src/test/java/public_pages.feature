Feature: Public pages & coupon contract (TC-KRT-PUB)

Background:
  * url baseUrl

Scenario: TC-KRT-PUB-001 homepage serves brand content
  Given path '/'
  When method get
  Then status 200
  And match response contains 'Anshita'

Scenario: TC-KRT-PUB-002 academy page serves
  Given path '/academy/'
  When method get
  Then status 200

Scenario: TC-KRT-PUB-003 sinha logo studio serves
  Given path '/sinha-logos/'
  When method get
  Then status 200

Scenario: TC-KRT-PUB-004 coupon contract exposes three layers
  Given path '/api/coupon/'
  When method get
  Then status 200
  And match response.ok == true
  And match response contains ['ok', 'coupon', 'default_coupon', 'exit_coupon']
  And match response.default_coupon.code == 'TODAYVIP'

Scenario: TC-KRT-PUB-005 CORS header present on public API
  Given path '/api/coupon/'
  When method get
  Then status 200
  And match header 'Access-Control-Allow-Origin' == '*'

Scenario: TC-KRT-PUB-006 language switch sets cookie
  Given path '/set-language/'
  And request { language: 'hindi' }
  When method post
  Then status 200
  And match response.language == 'hindi'
