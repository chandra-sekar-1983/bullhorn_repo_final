name        = "bullhorn"
description = "Bullhorn beta environment"
env         = "beta"
debug       = 0

github_repo_name   = "bullhorn"
github_repo_owner  = "dialpad"
github_branch_name = "main"

project_id     = "dp-bullhorn-integration"
project_name   = "dp-bullhorn-integration"
project_region = "us-central1"

cloud_run_regions         = ["us-east1"]
cloud_run_service_account = "iac-service-account@dp-bullhorn-integration.iam.gserviceaccount.com"

https_redirect = true
ssl            = true
domain         = "entegreeder.com"

features = {
  "dialpad" : {
    env_vars = {
      DIALPAD_URL = "https://dev-dot-integrations-dot-uv-beta.appspot.com"
    }
    secrets = ["DIALPAD_CLIENT_ID", "DIALPAD_CLIENT_SECRET"]
  }
  "external" : {
    env_vars = {
      EXTERNAL_SCOPE             = ""
      EXTERNAL_AUTHORIZATION_URL = "https://auth.bullhornstaffing.com/oauth/authorize"
      EXTERNAL_ACCESS_TOKEN_URL  = "https://auth.bullhornstaffing.com/oauth/token"
      EXTERNAL_REFRESH_TOKEN_URL = "https://auth.bullhornstaffing.com/oauth/token"
    }
    secrets = ["EXTERNAL_CLIENT_ID", "EXTERNAL_CLIENT_SECRET"]
  }
}

core_env_vars = {
  LOGGING_FORMATTER                   = "GCPFormatter"
  ORM_CLIENT                          = "core.orm.clients.datastore.DatastoreClient"
  REMOTE_LOCALHOST                    = 0
  SENTRY_DSN                          = "https://31a286965be747cc95088e90222164dc@o298232.ingest.sentry.io/6772543"
}
