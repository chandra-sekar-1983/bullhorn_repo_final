name            = "<NAME>"
description     = "<DESCRIPTION>"
env             = "production"
debug           = 0
private_version = false

github_repo_name   = "<GITHUB_REPO_NAME>"
github_repo_owner  = "<GITHUB_REPO_OWNER>"
github_branch_name = "<GITHUB_BRANCH_NAME>"

project_id     = "<PROJECT_ID>"
project_name   = "<PROJECT_NAME>"
project_region = "<PROJECT_REGION>"

cloud_run_regions         = []
cloud_run_service_account = "<CLOUD_RUN_SERVICE_ACCOUNT>"

https_redirect = false
ssl            = false

features = {
  "example-feature" : {
    env_vars = {}
    secrets  = []
  }
}

core_env_vars = {
  LOGGING_FORMATTER = "GCPFormatter"
  ORM_CLIENT        = "core.orm.clients.datastore.DatastoreClient"
  REMOTE_LOCALHOST  = 0
  SENTRY_DSN = "sentry-dsn"
}
