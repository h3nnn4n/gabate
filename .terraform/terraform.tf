terraform {
  backend "s3" {
    bucket = "h3nnn4n-terraform-state"
    key    = "gabate/"
    region = "us-east-1"
  }
}
