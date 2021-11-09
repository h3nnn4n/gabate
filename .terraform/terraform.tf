terraform {
  backend "s3" {
    bucket = "h3nnn4n-terraform-state"
    key    = "gabate/terraform_aws.tfstate"
    region = "us-east-1"
  }
}
