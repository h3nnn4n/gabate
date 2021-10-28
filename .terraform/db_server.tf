data "template_file" "user_data_db" {
  template = file("user_data_db.yml")
}

resource "hcloud_server" "db_server" {
  name        = "db-server"
  image       = var.os_type
  server_type = var.server_type
  location    = var.location
  ssh_keys    = [hcloud_ssh_key.default.id]
  labels = {
    type = "db_server"
  }
  user_data = data.template_file.user_data_db.rendered
}
