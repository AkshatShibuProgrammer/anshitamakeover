Feature: AI Concierge chatbot contract (TC-KRT-CHT)

Background:
  * url baseUrl

Scenario: TC-KRT-CHT-001 chatbot returns a reply and echoes session
  Given path '/api/chatbot/'
  And request { message: 'What are your bridal packages?', session_id: 'karate-session-1' }
  When method post
  Then status 200
  And match response.reply == '#present'
  And match response.session_id == 'karate-session-1'

Scenario: TC-KRT-CHT-002 empty message yields greeting
  Given path '/api/chatbot/'
  And request { message: '', session_id: 'karate-session-2' }
  When method post
  Then status 200
  And match response.reply == '#present'

Scenario: TC-KRT-CHT-003 budget below floor is defended
  Given path '/api/chatbot/'
  And request { message: 'I can only pay 20000' }
  When method post
  Then status 200
  And match response.reply contains '26,250'

Scenario: TC-KRT-CHT-004 budget above floor is accepted
  Given path '/api/chatbot/'
  And request { message: 'my budget is 30000' }
  When method post
  Then status 200
  And match response.reply contains '30,000'

Scenario: TC-KRT-CHT-005 malformed JSON never returns 500
  Given path '/api/chatbot/'
  And header Content-Type = 'application/json'
  And body '{not-valid-json'
  When method post
  Then status 200
  And match response.reply == '#present'
