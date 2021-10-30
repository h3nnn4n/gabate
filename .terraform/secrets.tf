data "aws_secretsmanager_secret_version" "creds" {
  secret_id = "gabate_celery_secrets"
}

locals {
  db_creds = jsondecode(
    data.aws_secretsmanager_secret_version.creds.secret_string
  )
}
