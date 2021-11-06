variable "aws_region" {
  default = "us-east-1"
}

variable "aws_access_key" {
  #default = ""
}

variable "aws_secret_key" {
  #default = ""
}

variable "aws_account" {
  #default = ""
}

variable "name" {
  default = "gabate"
}

variable "container_registry" {
  #default = ""
}

variable "container_image" {
  default = "gabate-worker"
}

variable "container_image_tag" {
  default = "latest"
}

variable "private_subnets" {
  default = [
    "10.0.1.0/24"
  ]
}

variable "public_subnets" {
  default = [
    "10.0.2.0/24"
  ]
}

variable "availability_zones" {
  default = [
    "us-east-1a",
    #"us-east-1b",
    #"us-east-1c",
    #"us-east-1d",
    #"us-east-1e",
    #"us-east-1f",
  ]
}

variable "rabbitmq_user" {}
variable "rabbitmq_password" {}
