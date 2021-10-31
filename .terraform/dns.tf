resource "aws_route53_zone" "h3nnn4n_me" {
  comment = "Primary domain"
  name = "h3nnn4n.me"

  lifecycle {
    prevent_destroy = true
  }
}

resource "aws_route53_record" "db_server" {
  zone_id = aws_route53_zone.h3nnn4n_me.zone_id
  name    = "gabate.h3nnn4n.me"
  type    = "A"
  ttl     = "60"
  records = [hcloud_server.db_server.ipv4_address]
}
