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
  default = "worker"
}

variable "container_image_tag" {
  default = "latest"
}
