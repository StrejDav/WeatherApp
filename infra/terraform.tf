terraform {
  cloud {
    organization = "StrejDav"

    workspaces {
      name    = "WeatherApp"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.28"
    }
  }

  required_version = ">= 1.4"
}
