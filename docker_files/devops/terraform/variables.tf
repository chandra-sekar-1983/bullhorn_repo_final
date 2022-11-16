variable "image_tag" {
  description = "Image tag: COMMIT SHA"
  type        = string
  default     = ""
}

variable "name" {
  description = "The Dialpad integration's name (App name)"
  type        = string
}

variable "description" {
  description = "Description of the app"
  type        = string
}

variable "env" {
  description = "Environment of the server intented to be interacted"
  type        = string
}

variable "secret" {
  description = "Secret value to be used to decode user bearer"
  type        = string
  default     = null
}

variable "debug" {
  description = "Whether debug mode is enabled"
  type        = number
  default     = 0
}

variable "github_repo_name" {
  description = "Repository name"
  type        = string
}

variable "github_repo_owner" {
  description = "Repository owner"
  type        = string
}

variable "github_branch_name" {
  description = "Branch name which trigger will be created to"
  type        = string
}

variable "project_id" {
  description = "The GCP project's information"
  type        = string
}

variable "project_name" {
  description = "The GCP project's information"
  type        = string
}

variable "project_region" {
  description = "The GCP project's information"
  type        = string
}

variable "cloud_run_regions" {
  description = "List of regions where the app will be deployed"
  type        = list(string)
}

variable "cloud_run_service_account" {
  description = "The email of a service account that creates cloud run"
  type        = string
}

variable "domain" {
  description = "Complete domain address. Leave undefined to use global LB ip address"
  type        = string
  default     = null
}

variable "https_redirect" {
  description = "Redirect calls from HTTP to HTTPS"
  type        = bool
  default     = false
}

variable "ssl" {
  description = "Enable SSL"
  type        = bool
  default     = false
}

variable "features" {
  description = "Features defined for the framework"
  type = map(object({
    secrets  = list(string)
    env_vars = map(string)
  }))
  default = {}
}

variable "core_env_vars" {
  description = "Environment variables to be defined"
  type        = map(string)
  default     = null
}

variable "core_secrets" {
  description = "Secrets for core"
  type        = list(string)
  default     = []
}

variable "private_version" {
  description = "Whether deploying a private version"
  type        = bool
  default     = false
}
