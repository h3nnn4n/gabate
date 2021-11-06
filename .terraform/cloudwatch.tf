resource "aws_cloudwatch_log_group" "main" {
  name              = "${var.name}-cloudwatch"
  retention_in_days = 30
}
