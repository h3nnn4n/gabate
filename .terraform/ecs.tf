# Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Service definitions
resource "aws_ecs_service" "main" {
 name                               = "${var.name}-worker"
 cluster                            = aws_ecs_cluster.main.id
 task_definition                    = aws_ecs_task_definition.main.arn
 desired_count                      = 1
 deployment_minimum_healthy_percent = 50
 deployment_maximum_percent         = 200
 launch_type                        = "FARGATE"
 scheduling_strategy                = "REPLICA"

 network_configuration {
   security_groups  = [aws_security_group.ecs_tasks.id]
   subnets          = aws_subnet.private.*.id
   assign_public_ip = false
 }

 lifecycle {
   ignore_changes = [task_definition, desired_count]
 }
}

resource "aws_ecs_service" "redis" {
 name                               = "${var.name}-redis"
 cluster                            = aws_ecs_cluster.main.id
 task_definition                    = aws_ecs_task_definition.redis.arn
 desired_count                      = 1
 deployment_minimum_healthy_percent = 50
 deployment_maximum_percent         = 200
 launch_type                        = "FARGATE"
 scheduling_strategy                = "REPLICA"

 network_configuration {
   security_groups  = [aws_security_group.ecs_tasks.id, aws_security_group.redis.id]
   subnets          = setunion(aws_subnet.private.*.id, aws_subnet.public.*.id)
   assign_public_ip = false
 }

 load_balancer {
   target_group_arn = aws_lb_target_group.redis.arn
   container_name   = "${var.name}-redis"
   container_port   = "6379"
 }


 lifecycle {
   ignore_changes = [task_definition, desired_count]
 }
}

# Task definitions
resource "aws_ecs_task_definition" "main" {
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  family                   = "${var.name}-worker"
  container_definitions = jsonencode([
    {
      name      = "${var.name}-worker"
      image     = "${var.container_registry}/${var.container_image}:${var.container_image_tag}"
      cpu       = 256
      memory    = 512
      essential = true
      environment = [
        {
          name = "BROKER_URL",
          value = "redis://${aws_alb.redis.dns_name}"
        },
        {
          name = "RESULT_BACKEND",
          value = "redis://${aws_alb.redis.dns_name}"
        },
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-stream-prefix = "ecs"
          awslogs-group         = aws_cloudwatch_log_group.main.name
          awslogs-region        = var.aws_region
        }
      }
    }
  ])
}

resource "aws_ecs_task_definition" "redis" {
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn            = aws_iam_role.ecs_task_role.arn
  family                   = "${var.name}-redis"
  container_definitions = jsonencode([
    {
      name      = "${var.name}-redis"
      image     = "redis:6.2"
      cpu       = 256
      memory    = 512
      essential = true
      environment = [
        {
          name = "foo",
          value = "bar"
        },
      ]
      portMappings = [
        {
          containerPort = 6379
        }
      ],
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-stream-prefix = "ecs"
          awslogs-group         = aws_cloudwatch_log_group.main.name
          awslogs-region        = var.aws_region
        }
      }
    }
  ])
}
