Feature: Pricing guardrails & auth boundary (TC-KRT-PRC / TC-KRT-AUTH)

Background:
  * url baseUrl

# ── pricing & negotiation guardrails (staff session) ────────────────────

Scenario: TC-KRT-PRC-001 AI negotiation clamps + restore
  Given path '/api/admin/price/'
  And cookie sessionid = sessionCookie
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-portal/'
  And header Content-Type = 'application/json'
  And request { type: 'ai_negotiation', ai_negotiation_min_floor_percent: 1, ai_max_discount_percent: 99 }
  When method post
  Then status 200
  And match response.ok == true
  And match response.ai_negotiation_min_floor_percent == 40
  And match response.ai_max_discount_percent == 50

  # restore canonical guardrails
  Given path '/api/admin/price/'
  And header Content-Type = 'application/json'
  And request { type: 'ai_negotiation', ai_negotiation_min_floor_percent: 75, ai_max_discount_percent: 20 }
  When method post
  Then match response.ok == true

Scenario: TC-KRT-PRC-002 booking offer rules clamp free sides 0..5
  Given path '/api/admin/price/'
  And cookie sessionid = sessionCookie
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-portal/'
  And header Content-Type = 'application/json'
  And request { type: 'booking_offer', free_sides: 99, combo_discount_percent: 80 }
  When method post
  Then status 200
  And match response.ok == true
  And match response.free_sides == 5
  And match response.combo_discount_percent == 30

  # restore
  Given path '/api/admin/price/'
  And header Content-Type = 'application/json'
  And request { type: 'booking_offer', free_sides: 2, combo_discount_percent: 15 }
  When method post
  Then match response.ok == true

Scenario: TC-KRT-PRC-003 coupon settings update + VIP lifecycle
  Given path '/api/admin/coupon/'
  And cookie sessionid = sessionCookie
  And cookie csrftoken = csrfToken
  And header X-CSRFToken = csrfToken
  And header Referer = baseUrl + '/admin-portal/'
  And header Content-Type = 'application/json'
  And request { coupon_active: '1', coupon_auto_by_date: '0', coupon_code: 'KARATE25', coupon_discount_percent: '25' }
  When method post
  Then match response.ok == true
  And match response.coupon_code == 'KARATE25'

  * def vipCode = 'KVIP' + java.util.UUID.randomUUID().toString().substring(0,4)
  Given path '/api/admin/coupon/'
  And header Content-Type = 'application/json'
  And request { action: 'generate_vip', code: '#(vipCode)', discount: 20 }
  When method post
  Then match response.ok == true

  Given path '/api/admin/coupon/'
  And header Content-Type = 'application/json'
  And request { action: 'delete_vip', code: '#(vipCode)' }
  When method post
  Then match response.ok == true

  # restore canonical seasonal coupon
  Given path '/api/admin/coupon/'
  And header Content-Type = 'application/json'
  And request { coupon_active: '1', coupon_auto_by_date: '0', coupon_code: 'GLAMOUR30', coupon_discount_percent: '30' }
  When method post
  Then match response.ok == true

# ── auth boundary (no session) ───────────────────────────────────────────

Scenario Outline: TC-KRT-AUTH-001 <path> requires staff login
  Given path '<path>'
  When method get
  Then status 302
  And match header Location contains '/admin-login/'

  Examples:
    | path                       |
    | /admin-portal/             |
    | /api/admin/coupon/         |
    | /api/admin/artist/         |
    | /api/admin/review/         |
    | /api/admin/media/          |
    | /api/admin/studio-service/ |
    | /api/admin/lookgroup/      |
    | /api/admin/service/        |
    | /api/admin/event-package/  |

Scenario: TC-KRT-AUTH-002 login page stays public
  Given path '/admin-login/'
  When method get
  Then status 200

Scenario: TC-KRT-AUTH-003 GET-only endpoints reject GET where POST required
  Given path '/api/chatbot/'
  When method get
  Then status 405
