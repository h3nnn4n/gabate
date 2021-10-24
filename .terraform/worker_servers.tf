data "template_file" "user_data" {
  template = file("user_data.yml")
}

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
  user_data = data.template_file.user_data.rendered
}
