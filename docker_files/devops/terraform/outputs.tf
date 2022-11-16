output "project_id" {
  value = var.project_id
}

# Display load balancer self link
output "lb_url" {
  value = local.ip_address
}

# Display backend service information
output "backend_service" {
  value = {
    "id" : google_compute_backend_service.default.id
    "self_link" : google_compute_backend_service.default.self_link
  }
}

# Url map self link
output "url_maps_self_link" {
  value = google_compute_url_map.default.self_link
}
