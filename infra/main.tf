provider "aws" {
  region = "eu-north-1"
}

data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd-gp3/ubuntu-noble-24.04-amd64-server-*"]
  }

  owners = ["099720109477"]
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = "t3.micro"

  key_name = "david-new"

  subnet_id                   = aws_subnet.subnet_public.id
  associate_public_ip_address = true

  vpc_security_group_ids = [aws_security_group.sg_internet_facing.id]

  tags = {
    Name = "weatherapp-app"
  }
}
