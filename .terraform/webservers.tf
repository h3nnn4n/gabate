resource "hcloud_server" "worker" {
  count       = var.instances
  name        = "worker-${count.index}"
  image       = var.os_type
  server_type = var.server_type
  location    = var.location
  ssh_keys    = [hcloud_ssh_key.default.id]
  labels = {
    type = "workers"
  }
  user_data = file("user_data.yml")
}
