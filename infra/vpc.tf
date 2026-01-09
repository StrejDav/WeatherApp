resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "weatherapp-vpc"
  }
}

resource "aws_subnet" "subnet_public" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.101.0/24"
  availability_zone = "eu-north-1a"

  tags = {
    Name = "weatherapp-subnet-public"
  }
}

resource "aws_subnet" "subnet_private_a" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.1.0/24"
  availability_zone = "eu-north-1a"

  tags = {
    Name = "weatherapp-subnet-private-a"
  }
}

resource "aws_subnet" "subnet_private_b" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "eu-north-1b"

  tags = {
    Name = "weatherapp-subnet-private-b"
  }
}

resource "aws_db_subnet_group" "subnet_db" {
  name        = "weatherapp-subnet-group-db"
  description = "Subnet group for RDS for WeatherApp"

  subnet_ids = [aws_subnet.subnet_private_a.id, aws_subnet.subnet_private_b.id]

  tags = {
    Name = "weatherapp-subnet-private"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "weatherapp-igw"
  }
}

resource "aws_route_table" "rt_public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = aws_vpc.main.cidr_block
    gateway_id = "local"
  }

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name = "weatherapp-rt-public"
  }
}

resource "aws_route_table_association" "rt_public_assoc" {
  subnet_id      = aws_subnet.subnet_public.id
  route_table_id = aws_route_table.rt_public.id
}

resource "aws_security_group" "sg_internet_facing" {
  name        = "allow-http-ssh"
  description = "Allows inbound HTTP and SSH and all outbound traffic"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "weatherapp-sg-internet-facing"
  }
}

resource "aws_security_group" "sg_db_internal" {
  name        = "allow-postgres"
  description = "Allows PostgreSQL traffic from inside the private subnet"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.subnet_private_a.cidr_block, aws_subnet.subnet_private_b.cidr_block]
  }

  egress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [aws_subnet.subnet_private_a.cidr_block, aws_subnet.subnet_private_b.cidr_block]
  }

  tags = {
    Name = "weatherapp-sg-postgres-internal"
  }
}
