data "template_file" "user_data" {
  template = file("worker_user_data/user_data.yml")
}

data "template_file" "start_worker" {
  template = file("worker_user_data/start_worker.sh")
}

data "template_cloudinit_config" "config" {
  gzip          = false
  base64_encode = false

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.user_data.rendered
  }

  part {
    content_type = "text/x-shellscript"
    content      = <<-EOF
    #!/bin/bash
    echo '${hcloud_server.db_server.ipv4_address}' > /opt/db_server_ip
    EOF
  }

  part {
    content_type = "text/x-shellscript"
    content      = data.template_file.start_worker.rendered
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
