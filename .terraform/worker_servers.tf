data "template_file" "user_data" {
  template = file("worker_user_data/user_data.yml")
}

data "template_file" "setup_worker_env" {
  template = file("worker_user_data/setup_worker_env.sh")
}

data "template_cloudinit_config" "config" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/x-shellscript"
    content      = <<-EOF
    #!/bin/bash
    echo '${local.db_creds.rabbitmq_user}' > /opt/rabbitmq_user
    echo '${local.db_creds.rabbitmq_passwd}' > /opt/rabbitmq_passwd

    echo '${local.db_creds.redis_user}' > /opt/redis_user
    echo '${local.db_creds.redis_passwd}' > /opt/redis_passwd

    echo '${local.db_creds.rom_gpg_key}' > /opt/rom_gpg_key

    echo '${local.db_creds.aws_api_key}' > /opt/aws_api_key
    echo '${local.db_creds.aws_secret_key}' > /opt/aws_secret_key
    EOF
  }

  part {
    content_type = "text/x-shellscript"
    content      = data.template_file.setup_worker_env.rendered
  }

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.user_data.rendered
  }
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
  user_data = data.template_cloudinit_config.config.rendered
}
