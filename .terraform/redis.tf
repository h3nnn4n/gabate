resource "aws_security_group" "default" {
  name_prefix = "${var.aws_namespace}"
  vpc_id      = "${aws_vpc.default.id}"

  ingress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_elasticache_subnet_group" "default" {
  name       = "${var.aws_namespace}-cache-subnet"
  subnet_ids = ["${aws_subnet.default.id}"]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "gabate"
  engine               = "redis"
  node_type            = "cache.t2.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  engine_version       = "6.x"
  port                 = 6379
  apply_immediately    = true
  subnet_group_name    = "${aws_elasticache_subnet_group.default.name}"
}
