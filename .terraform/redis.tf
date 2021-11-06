# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/elasticache_cluster
resource "aws_elasticache_cluster" "example" {
  cluster_id           = "${var.name}-result-backend"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  engine_version       = "6.x"
  port                 = 6379
  security_groups      = [aws_security_group.message-broker.id]
  apply_immediately    = true
  availability_zone    = var.availability_zones[0]
}
