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
