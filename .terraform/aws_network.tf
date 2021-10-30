resource "aws_vpc" "default" {
  cidr_block           = "${var.aws_vpc_cidr_block}"
  enable_dns_hostnames = true
}

resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.default.id}"
}

resource "aws_route" "internet_access" {
  route_table_id         = "${aws_vpc.default.main_route_table_id}"
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = "${aws_internet_gateway.default.id}"
}

data "aws_availability_zones" "available" {}

resource "aws_subnet" "default" {
  #count                   = "${length(var.aws_cidr_blocks)}"
  vpc_id                  = "${aws_vpc.default.id}"
  availability_zone       = "${data.aws_availability_zones.available.names[0]}"
  cidr_block              = "${var.aws_cidr_blocks[0]}"
  map_public_ip_on_launch = true
}
