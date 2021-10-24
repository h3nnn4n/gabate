output "workers_servers_status" {
  value = {
    for server in hcloud_server.worker :
    server.name => server.status
  }
}

output "workers_servers_ips" {
  value = {
    for server in hcloud_server.worker :
    server.name => server.ipv4_address
  }
}

output "db_server_status" {
  value = {
    for server in hcloud_server.db_server :
    server.name => server.status
  }
}

output "db_server_ips" {
  value = {
    for server in hcloud_server.db_server :
    server.name => server.ipv4_address
  }
}
