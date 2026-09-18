Feature: Admin CRUD contract — packages, events, artists, services, media (TC-KRT-ADM)

Background:
  * url baseUrl
  * cookie sessionid = sessionCookie
  * cookie csrftoken = csrfToken
  * header X-CSRFToken = csrfToken
  * header Referer = baseUrl + '/admin-portal/'
  * def suffix = java.util.UUID.randomUUID().toString().substring(0,8)

Scenario: TC-KRT-ADM-001 package create → update → delete
  * def pkgName = 'Karate Suite ' + suffix
  Given path '/api/admin/service/'
  And header Content-Type = 'application/json'
  And request { name: '#(pkgName)', package_type: 'party', price: '7000', features: 'Karate probe feature' }
  When method post
  Then status 200
  And match response.ok == true
  And match response.package.price_label == '₹7,000'
  * def pkgId = response.package.id

  Given path '/api/admin/service/'
  And header Content-Type = 'application/json'
  And request { id: '#(pkgId)', name: '#(pkgName + " v2")', price: '8000' }
  When method post
  Then match response.ok == true

  Given path '/api/admin/service/'
  And header Content-Type = 'application/json'
  And request { action: 'delete', id: '#(pkgId)' }
  When method post
  Then match response.ok == true

Scenario: TC-KRT-ADM-002 event package returns commission maths
  * def evtName = 'Karate Bundle ' + suffix
  Given path '/api/admin/event-package/'
  And header Content-Type = 'application/json'
  And request { name: '#(evtName)', category: 'photography', package_type: 'custom', vendor_cost: '50000', price: '68000' }
  When method post
  Then status 200
  And match response.ok == true
  And match response.commission == 18000.0
  And match response.roi_pct == 36.0
  * def evtId = response.id

  Given path '/api/admin/event-package/'
  And header Content-Type = 'application/json'
  And request { id: '#(evtId)' }
  When method delete
  Then match response.ok == true

Scenario: TC-KRT-ADM-003 artist create → list → delete
  * def artistName = 'Karate Artist ' + suffix
  Given path '/api/admin/artist/'
  And form field name = artistName
  And form field specialities = 'makeup'
  When method post
  Then status 200
  And match response.ok == true
  * def artistId = response.artist.id

  Given path '/api/admin/artist/'
  When method get
  Then match response.artists[*].id contains artistId

  Given path '/api/admin/artist/'
  And form field action = 'delete'
  And form field id = artistId
  When method post
  Then match response.ok == true

Scenario: TC-KRT-ADM-004 studio service create → delete with features list
  * def svcTitle = 'Karate Discipline ' + suffix
  Given path '/api/admin/studio-service/'
  And form field title = svcTitle
  And form field price = '9000'
  And form field description = 'karate probe'
  And form field features = 'alpha\nbeta'
  When method post
  Then status 200
  And match response.ok == true
  And match response.service.features_list == ['alpha', 'beta']
  * def svcId = response.service.id

  Given path '/api/admin/studio-service/'
  And form field action = 'delete'
  And form field id = svcId
  When method post
  Then match response.ok == true

Scenario: TC-KRT-ADM-005 look group + youtube media attach → teardown
  * def grpName = 'Karate Group ' + suffix
  Given path '/api/admin/lookgroup/'
  And form field name = grpName
  And form field client_name = 'Karate Client'
  And form field makeup_type = 'Probe Look'
  And form field category = 'bridal'
  When method post
  Then status 200
  And match response.ok == true
  * def grpId = response.group.id

  Given path '/api/admin/lookgroup/media/'
  And form field group_id = grpId
  And form field media_type = 'youtube'
  And form field external_url = 'https://youtu.be/abcdefghijk'
  When method post
  Then status 200
  And match response.ok == true
  And match response.item.embed_code == 'abcdefghijk'

  Given path '/api/admin/lookgroup/'
  And form field action = 'delete'
  And form field id = grpId
  When method post
  Then match response.ok == true

Scenario: TC-KRT-ADM-006 instagram shortcode extraction
  * def mediaTitle = 'Karate Reel ' + suffix
  Given path '/api/admin/media/'
  And form field title = mediaTitle
  And form field media_type = 'instagram'
  And form field external_url = 'https://www.instagram.com/reel/Dxyz123AbCd/'
  And form field section = 'reels'
  When method post
  Then status 200
  And match response.ok == true
  And match response.item.embed_code == 'Dxyz123AbCd'
  * def mediaId = response.item.id

  Given path '/api/admin/media/'
  And header Content-Type = 'application/json'
  And request { action: 'delete', id: '#(mediaId)' }
  When method post
  Then match response.ok == true
