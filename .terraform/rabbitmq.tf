# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/mq_broker
resource "aws_mq_broker" "example" {
  broker_name = "${var.name}-message-broker"

  engine_type        = "RabbitMQ"
  engine_version     = "3.8.22"
  host_instance_type = "mq.t3.micro"
  security_groups    = [aws_security_group.message-broker.id]
  apply_immediately  = true
  subnet_ids         = aws_subnet.private.*.id
  deployment_mode    = "SINGLE_INSTANCE"

  user {
    username = var.rabbitmq_user
    password = var.rabbitmq_password
  }
}
