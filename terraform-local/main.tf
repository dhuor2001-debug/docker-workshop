terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

# Create a private network for the containers to communicate
resource "docker_network" "zoomcamp_network" {
  name = "pg-network"
}

# 1. PostgreSQL Database Container
resource "docker_image" "postgres" {
  name         = "postgres:13"
  keep_locally = false
}

resource "docker_container" "postgres_db" {
  name  = "pg-database"
  image = docker_image.postgres.image_id

  # These are the default credentials from the Zoomcamp
  env = [
    "POSTGRES_USER=root",
    "POSTGRES_PASSWORD=root",
    "POSTGRES_DB=ny_taxi"
  ]

  ports {
    internal = 5432
    external = 5432
  }

  networks_advanced {
    name = docker_network.zoomcamp_network.name
  }
}

# 2. pgAdmin Interface Container
resource "docker_image" "pgadmin" {
  name         = "dpage/pgadmin4"
  keep_locally = false
}

resource "docker_container" "pgadmin_ui" {
  name  = "pgadmin-ui"
  image = docker_image.pgadmin.image_id

  env = [
    "PGADMIN_DEFAULT_EMAIL=admin@admin.com",
    "PGADMIN_DEFAULT_PASSWORD=root"
  ]

  # Using port 8080 for the UI since it is standard
  ports {
    internal = 80
    external = 8088
  }

  networks_advanced {
    name = docker_network.zoomcamp_network.name
  }
}