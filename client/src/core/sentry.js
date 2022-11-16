import * as Sentry from "@sentry/vue";
import { BrowserTracing } from "@sentry/tracing";

class SentryClient {
  constructor(app, router, { options } = {}) {
    Sentry.init({
      app,
      dsn: process.env.SENTRY_DSN,
      // Alternatively, use `process.env.npm_package_version` for a dynamic release version
      // if your build tool supports it.
      release: process.env.NAME + '@' + process.env.COMMIT_SHA,
      environment: process.env.ENV,
      integrations: [
        new BrowserTracing({
          routingInstrumentation: Sentry.vueRouterInstrumentation(router),
          tracingOrigins: ["localhost", /^\//],
        }),
      ],
      // Set tracesSampleRate to 1.0 to capture 100%
      // of transactions for performance monitoring.
      // We recommend adjusting this value in production
      tracesSampleRate: 1.0,
      ...options,
    });
  }
}

export {
  SentryClient
}
