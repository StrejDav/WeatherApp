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

data "aws_kms_key" "db_key" {
  key_id = "arn:aws:kms:eu-north-1:361966322279:key/3bba199d-531d-4069-ab0e-bd873d03240b"
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

resource "aws_db_instance" "default" {
  identifier                    = "weatherapp-db"
  multi_az                      = false
  db_subnet_group_name          = aws_db_subnet_group.subnet_db.id
  vpc_security_group_ids        = [aws_security_group.sg_db_internal.id]
  allocated_storage             = 20
  db_name                       = "weatherdata"
  engine                        = "postgres"
  engine_version                = "18.1"
  instance_class                = "db.t3.micro"
  username                      = "postgres"
  skip_final_snapshot           = true
  manage_master_user_password   = true
  master_user_secret_kms_key_id = data.aws_kms_key.db_key.key_id
}
