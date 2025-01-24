# variable "yc_token" {
#   type        = string
#   description = "Yandex Cloud OAuth token"
# }

# variable "yc_cloud_id" {
#   type = string
#   description = "Yandex Cloud ID"
# }

# variable "yc_folder_id" {
#   type        = string
#   description = "Yandex Cloud Folder ID"
# }

variable "provider_config" {
  description = "Yandex Cloud configuration"
  type = object({
    zone      = string
    folder_id = string
    token     = string
    cloud_id  = string
  })
}

# из yandex_vpc_network.network.id
variable "network_id" {
  type        = string
  description = "id of network"
}

variable "subnet_id" {
  type        = string
  description = "id of subnet"
}

variable "yc_zone" {
  type        = string
  description = "Zone for Yandex Cloud resources"
}
# из terraform.tfvars
variable "yc_subnet_name" {
  type        = string
  description = "Name of the custom subnet"
}
# из terraform.tfvars
variable "yc_network_name" {
  type        = string
  description = "Name of the network"
}

# variable "yc_subnet_range" {
#   type        = string
#   description = "CIDR block for the subnet"
# }

# из terraform.tfvars
variable "yc_postgresql_cluster_name" {
  type        = string
  description = "Name of the PostGre cluster"
}
# из terraform.tfvars
variable "yc_postgresql_version" {
  type        = string
  description = "Version of PostGre"
}
# из terraform.tfvars
variable "yc_postgresql_environment" {
  type        = string
  description = "Environment of PostGre"
}
# из terraform.tfvars
variable "postgresql_database_name" {
  type        = string
  description = "Name of the PostGre database"
}
# из terraform.tfvars
variable "postgresql_user_name" {
  type        = string
  description = "Name of the PostGre user"
}
# из terraform.tfvars
variable "postgresql_user_password" {
  type        = string
  description = "Password of the PostGre user"
}
# default
variable "postgresql_resource_preset_id" {
  description = "Resource preset for PostGre cluster"
  type        = string
  default     = "s2.micro"
}
# default
variable "postgresql_disk_type_id" {
  description = "Disk type for PostGre cluster"
  type        = string
  default     = "network-ssd"
}
# default
variable "postgresql_disk_size" {
  description = "Disk size for PostGre cluster in GB"
  type        = number
  default     = 16
}
# default
variable "postgresql_config" {
  description = "MySQL configuration"
  type = object({
    shared_preload_libraries       = string
    max_connections                = number
    default_transaction_isolation  = string
    enable_parallel_hash           = bool
    autovacuum_vacuum_scale_factor = number
  })
  default = {
    default_transaction_isolation  = "TRANSACTION_ISOLATION_READ_COMMITTED"
    max_connections                = 100
    shared_preload_libraries       = "SHARED_PRELOAD_LIBRARIES_AUTO_EXPLAIN,SHARED_PRELOAD_LIBRARIES_PG_HINT_PLAN"
    enable_parallel_hash           = true
    autovacuum_vacuum_scale_factor = 0.34
  }
}

# variable "yc_service_account_name" {
#   type        = string
#   description = "Name of the service account"
# }

# variable "yc_bucket_name" {
#   type        = string
#   description = "Name of the bucket"
# }
