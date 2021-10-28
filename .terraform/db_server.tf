data "template_file" "db_user_data" {
  template = file("db_user_data/user_data.yml")
}

data "template_cloudinit_config" "db_config" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.db_user_data.rendered
  }

  part {
    content_type = "text/x-shellscript"
    content      = <<-EOF
    #!/bin/bash
    sudo rabbitmqctl add_user ${local.db_creds.rabbitmq_user} ${local.db_creds.rabbitmq_passwd}
    sudo rabbitmqctl set_user_tags ${local.db_creds.rabbitmq_user} administrator
    sudo rabbitmqctl set_permissions -p / ${local.db_creds.rabbitmq_user} ".*" ".*" ".*"
    EOF
  }
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
  user_data = data.template_cloudinit_config.db_config.rendered
}
