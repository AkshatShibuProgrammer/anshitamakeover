function fn() {
  // Base URL of a running Anshita Makeover Django server.
  // Override with: mvn test -DbaseUrl=http://host:port
  var baseUrl = karate.properties['baseUrl'] || 'http://127.0.0.1:8111';

  karate.configure({
    connectTimeout: 15000,
    readTimeout: 30000
  });

  var config = {
    baseUrl: baseUrl,
    adminUser: 'regadmin',
    adminPass: 'RegTest@2026'
  };

  // Pre-authenticate once for the whole suite and reuse the session.
  var login = karate.callSingle('classpath:helpers/admin-login.feature', config);
  config.sessionCookie = login.sessionCookie;
  config.csrfToken = login.csrfToken;
  return config;
}
