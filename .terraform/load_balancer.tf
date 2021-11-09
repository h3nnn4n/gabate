resource "aws_lb_target_group" "redis" {
  name        = "redis-target-group"
  port        = 6379
  protocol    = "TCP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  depends_on = [aws_alb.redis]
}

resource "aws_alb" "redis" {
  name               = "redis-lb"
  internal           = false
  load_balancer_type = "network"

  subnets = aws_subnet.public.*.id

  depends_on = [aws_internet_gateway.main]
}

resource "aws_alb_listener" "redis_tcp" {
  load_balancer_arn = aws_alb.redis.arn
  port              = "6379"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.redis.arn
  }
}

output "redis_lb_url" {
  value = aws_alb.redis.dns_name
}
