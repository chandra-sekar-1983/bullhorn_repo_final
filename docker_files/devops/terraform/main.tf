locals {
  registry      = "${var.project_region}-docker.pkg.dev"
  registry_repo = "${var.name}-repo"
  image_base    = "${local.registry}/${var.project_id}/${local.registry_repo}/${var.name}"
  ip_address    = google_compute_global_address.default.address
  base_url      = var.ssl ? "https://${var.name}.${var.domain}" : "http://${local.ip_address}"
  env_vars = merge(
    merge([for feature, options in var.features : options.env_vars]...),
    tomap(var.core_env_vars)
  )
  secret_names = toset(
    concat(
      flatten([
        for feature, options in var.features : [
          for secret in options.secrets : secret
        ]
      ]),
      var.core_secrets
    )
  )
  secrets = tomap({
    for secret in local.secret_names : "${secret}" => coalesce(
      lookup(local.env_vars, secret, null),
      data.google_secret_manager_secret_version.secrets["${secret}"].secret_data
    )
  })
  var_file_name = var.private_version ? var.name : var.env
}


terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 3.53"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 3.53"
    }
  }
  required_version = ">= 0.13"
  backend "gcs" {}
}

provider "google" {
  project         = var.project_id
  region          = var.project_region
  request_timeout = "60s"
}

provider "google-beta" {
  project         = var.project_id
  region          = var.project_region
  request_timeout = "60s"
}

data "google_secret_manager_secret_version" "secrets" {
  for_each = length(local.secret_names) > 0 ? local.secret_names : toset([])
  provider = google-beta
  secret   = each.value
}

resource "google_storage_bucket" "logs_bucket" {
  name          = "${var.name}-logs-bucket"
  location      = var.project_region
  force_destroy = true
}

resource "google_storage_bucket" "static_bucket" {
  name          = "${var.name}-static-bucket"
  location      = var.project_region
  force_destroy = true
}

data "google_iam_policy" "viewer" {
  binding {
    role = "roles/storage.objectViewer"
    members = [
      "allUsers",
    ]
  }
}

resource "google_storage_bucket_iam_policy" "viewer" {
  bucket      = google_storage_bucket.static_bucket.name
  policy_data = data.google_iam_policy.viewer.policy_data
}

resource "google_compute_backend_bucket" "static_backend" {
  name        = "${var.name}-static-backend-bucket"
  bucket_name = google_storage_bucket.static_bucket.name
  enable_cdn  = true
}

resource "google_cloudbuild_trigger" "build_trigger" {
  name = "${var.name}-trigger"
  build {

    step {
      id   = "init"
      name = "hashicorp/terraform:latest"
      args = [
        "-chdir=./devops/terraform",
        "init",
        "-reconfigure",
        "-backend-config=bucket=${var.name}-tfstate"
      ]
      wait_for = ["-"]
    }

    step {
      id         = "build-static"
      name       = "node:16.14.2-bullseye-slim"
      entrypoint = "bash"
      args = [
        "-c",
        <<-EOT
        cd ./client \
        && npm install \
        && npm run ${var.env} -- --env STATIC_PATH=/workspace/static
        EOT
      ]
      env = [
        for k, v in merge(
          local.env_vars,
          {
            ENV        = "${var.env}",
            NAME       = "${var.name}",
            DEBUG      = "${var.debug}",
            BASE_URL   = "${local.base_url}",
            COMMIT_SHA = "$COMMIT_SHA"
        }) : "${k}=${v}"
      ]
      wait_for = ["-"]
    }

    step {
      id         = "push-static"
      name       = "gcr.io/cloud-builders/gsutil"
      entrypoint = "gsutil"
      args = [
        "-m",
        "rsync",
        "-r",
        "/workspace/static/",
        "gs://${google_storage_bucket.static_bucket.name}/static",
      ]
      wait_for = ["build-static"]
    }

    step {
      id         = "build"
      name       = "gcr.io/cloud-builders/docker"
      entrypoint = "bash"
      args = [
        "-c",
        <<-EOT
        mkdir -p ./templates \
          && cp /workspace/static/index.html ./server/templates/index.html \
          && docker build \
            --tag ${local.image_base}:$COMMIT_SHA \
            -f ./docker_files/${var.env}.Dockerfile .
        EOT
      ]
      wait_for = ["build-static"]
    }

    step {
      id       = "push"
      name     = "gcr.io/cloud-builders/docker"
      args     = ["push", "${local.image_base}:$COMMIT_SHA"]
      wait_for = ["build"]
    }

    step {
      id   = "plan"
      name = "hashicorp/terraform:latest"
      args = [
        "-chdir=./devops/terraform",
        "plan",
        "-var=image_tag=$COMMIT_SHA",
        "-var-file=./vars/${local.var_file_name}.tfvars",
        "-out=tf.plan",
      ]
      wait_for = ["init"]
    }

    step {
      id   = "apply"
      name = "hashicorp/terraform:latest"
      args = [
        "-chdir=./devops/terraform",
        "apply",
        "-auto-approve",
        "tf.plan",
      ]
      wait_for = ["plan", "push"]
    }

    logs_bucket = google_storage_bucket.logs_bucket.name
  }

  github {
    owner = var.github_repo_owner
    name  = var.github_repo_name
    push {
      branch = var.github_branch_name
    }
  }
  service_account = "projects/${var.project_id}/serviceAccounts/${var.cloud_run_service_account}"
}

resource "google_compute_backend_service" "default" {
  provider                        = google-beta
  project                         = var.project_id
  name                            = "${var.name}-backend"
  description                     = null
  connection_draining_timeout_sec = null
  enable_cdn                      = false
  custom_request_headers          = []
  custom_response_headers         = []
  security_policy                 = null

  dynamic "backend" {
    for_each = google_compute_region_network_endpoint_group.serverless_neg
    content {
      description = "${var.name} ${backend.value.id} backend"
      group       = backend.value.id
    }
  }
  log_config {
    enable      = true
    sample_rate = 1.0
  }
}

### IPv4 block ###
resource "google_compute_global_forwarding_rule" "http" {
  project    = var.project_id
  name       = var.name
  target     = google_compute_target_http_proxy.default.self_link
  ip_address = local.ip_address
  port_range = "80"
}

resource "google_compute_global_forwarding_rule" "https" {
  project    = var.project_id
  count      = var.ssl ? 1 : 0
  name       = "${var.name}-https"
  target     = google_compute_target_https_proxy.default[0].self_link
  ip_address = local.ip_address
  port_range = "443"
}

resource "google_compute_global_address" "default" {
  project    = var.project_id
  name       = "${var.name}-address"
  ip_version = "IPV4"
}

### IPv4 block ###

# HTTP proxy when http forwarding is true
resource "google_compute_target_http_proxy" "default" {
  project = var.project_id
  name    = "${var.name}-http-proxy"
  url_map = (
    var.https_redirect == false ? (
      google_compute_url_map.default.self_link
      ) : (
      join("", google_compute_url_map.https_redirect.*.self_link)
    )
  )
}

# HTTPS proxy when ssl is true
resource "google_compute_target_https_proxy" "default" {
  project          = var.project_id
  count            = var.ssl ? 1 : 0
  name             = "${var.name}-https-proxy"
  url_map          = google_compute_url_map.default.self_link
  ssl_certificates = compact(google_compute_managed_ssl_certificate.default.*.self_link)
}

resource "google_dns_managed_zone" "zone" {
  count    = var.private_version ? 0 : 1
  name     = replace("${var.project_id}-zone", ".", "-")
  dns_name = "${var.domain}."
}

data "google_dns_managed_zone" "zone" {
  count = var.private_version ? 1 : 0
  name  = replace("${var.project_id}-zone", ".", "-")
}

resource "google_dns_record_set" "arecord" {
  count        = var.private_version ? 0 : 1
  name         = "${var.name}.${var.domain}."
  type         = "A"
  ttl          = 3600
  managed_zone = google_dns_managed_zone.zone[0].name
  rrdatas      = [google_compute_global_forwarding_rule.https[0].ip_address]
}

resource "google_dns_record_set" "arecord-private" {
  count        = var.private_version ? 1 : 0
  name         = "${var.name}.${var.domain}."
  type         = "A"
  ttl          = 3600
  managed_zone = data.google_dns_managed_zone.zone[0].name
  rrdatas      = [google_compute_global_forwarding_rule.https[0].ip_address]
}

resource "google_compute_managed_ssl_certificate" "default" {
  provider = google-beta
  project  = var.project_id
  count    = var.ssl ? 1 : 0
  name     = replace("${var.name}-${var.domain}-cert", ".", "-")

  lifecycle {
    create_before_destroy = true
  }

  managed {
    domains = ["${var.name}.${var.domain}"]
  }
}

resource "google_compute_url_map" "default" {
  project         = var.project_id
  name            = "${var.name}-url-map"
  default_service = google_compute_backend_service.default.id

  host_rule {
    hosts        = var.ssl ? ["${var.name}.${var.domain}", local.ip_address] : [local.ip_address]
    path_matcher = var.name
  }

  path_matcher {
    name            = var.name
    default_service = google_compute_backend_service.default.id
    path_rule {
      paths   = ["/static/*"]
      service = google_compute_backend_bucket.static_backend.id
    }
  }
}

resource "google_compute_url_map" "https_redirect" {
  project = var.project_id
  count   = var.https_redirect ? 1 : 0
  name    = "${var.name}-https-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  for_each              = google_cloud_run_service.service
  provider              = google-beta
  name                  = "serverless-neg-${each.value.name}-${each.value.location}"
  network_endpoint_type = "SERVERLESS"
  project               = each.value.project
  region                = each.value.location
  cloud_run {
    service = each.value.name
  }
}

resource "google_cloud_run_service_iam_member" "public_access" {
  for_each = google_cloud_run_service.service
  location = each.value.location
  project  = each.value.project
  service  = each.value.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service" "service" {
  for_each = toset(var.cloud_run_regions)
  name     = var.name
  location = each.value
  project  = var.project_id
  template {
    spec {
      service_account_name = var.cloud_run_service_account
      containers {
        image = "${local.image_base}:${var.image_tag}"
        env {
          name  = "NAME"
          value = var.name
        }
        env {
          name  = "ENV"
          value = var.env
        }
        env {
          name  = "DEBUG"
          value = var.debug
        }
        env {
          name  = "BASE_URL"
          value = local.base_url
        }
        dynamic "env" {
          for_each = merge(local.env_vars, local.secrets)
          content {
            name  = env.key
            value = env.value
          }
        }
      }
    }
  }
}

resource "google_pubsub_topic" "log_aggregation_topic" {
  count = var.private_version ? 0 : 1
  name  = "log-aggregation"
}

resource "google_pubsub_subscription" "log_ingest" {
  count                        = var.private_version ? 0 : 1
  name                         = "log-ingest"
  ack_deadline_seconds         = 60
  topic                        = google_pubsub_topic.log_aggregation_topic[0].name
}

resource "google_pubsub_subscription_iam_member" "owner" {
  subscription = google_pubsub_subscription.log_ingest[0].name
  role         = "roles/owner"
  member       = "serviceAccount:${var.cloud_run_service_account}"
}

resource "google_pubsub_topic_iam_member" "owner" {
  project = var.project_id
  topic = google_pubsub_topic.log_aggregation_topic[0].name
  role = "roles/owner"
  member = "serviceAccount:${var.cloud_run_service_account}"
}

resource "google_logging_project_sink" "log_aggregation" {
  count       = var.private_version ? 0 : 1
  name        = "log-aggregration"
  destination = "pubsub.googleapis.com/projects/${var.project_id}/topics/${google_pubsub_topic.log_aggregation_topic[0].name}"
  description = "Route Logs for Log Aggregation Ingest pipeline"
}

