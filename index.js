// When using npm, import Sentry
import * as Sentry from '@sentry/browser';

//Options which can be read from an environment variable or your ~/.sentryclirc file
const SENTRY_DSN_BIND = {SENTRY_DSN}
//export SENTRY_DSN=sdns
Sentry.init({
  dsn: SENTRY_DSN_BIND,
  maxBreadcrumbs: 50,
  debug: true,
});


Sentry.captureException(new Error("Something broke"));
throw new Error('Something broke');
