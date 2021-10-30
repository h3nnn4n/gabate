data "template_file" "db_user_data" {
  template = file("db_user_data/user_data.yml")
}

data "template_cloudinit_config" "db_config" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/x-shellscript"
    content      = <<-EOF
    #!/bin/sh
    echo '${local.db_creds.rabbitmq_user}' > /opt/rabbitmq_user
    echo '${local.db_creds.rabbitmq_passwd}' > /opt/rabbitmq_passwd
    echo '${local.db_creds.redis_user}' > /opt/redis_user
    echo '${local.db_creds.redis_passwd}' > /opt/redis_passwd
    EOF
  }

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.db_user_data.rendered
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
