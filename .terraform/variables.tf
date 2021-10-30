# Hetzner cloud stuff

variable "hcloud_token" {
  #default = ""
}

variable "location" {
  default = "nbg1"
}

variable "http_protocol" {
  default = "http"
}

variable "http_port" {
  default = "80"
}

variable "instances" {
  default = "1"
}

variable "server_type" {
  default = "cx11"
}

variable "os_type" {
  default = "ubuntu-20.04"
}

variable "disk_size" {
  default = "20"
}

variable "ip_range" {
  default = "10.0.1.0/24"
}

# Aws stuff

variable "aws_namespace" {
  default = "gabate"
}

variable "aws_vpc_cidr_block" {
  description = "The top-level CIDR block for the VPC."
  default     = "10.1.0.0/16"
}

variable "aws_cidr_blocks" {
  description = "The CIDR blocks to create the workstations in."
  default     =  ["10.1.1.0/24", "10.1.2.0/24"]
}

variable "aws_region" {
  default = "us-east-1"
}

variable "aws_access_key" {
  #default = ""
}

variable "aws_secret_key" {
  #default = ""
}
