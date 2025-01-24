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
variable "yc_mysql_cluster_name" {
  type        = string
  description = "Name of the MySQL cluster"
}
# из terraform.tfvars
variable "yc_mysql_version" {
  type        = string
  description = "Version of MySQL"
}
# из terraform.tfvars
variable "yc_mysql_environment" {
  type        = string
  description = "Environment of MySQL"
}
# из terraform.tfvars
variable "mysql_database_name" {
  type        = string
  description = "Name of the MySQL database"
}
# из terraform.tfvars
variable "mysql_user_name" {
  type        = string
  description = "Name of the MySQL user"
}
# из terraform.tfvars
variable "mysql_user_password" {
  type        = string
  description = "Password of the MySQL user"
}
# default
variable "mysql_resource_preset_id" {
  description = "Resource preset for MySQL cluster"
  type        = string
  default     = "s2.micro"
}
# default
variable "mysql_disk_type_id" {
  description = "Disk type for MySQL cluster"
  type        = string
  default     = "network-ssd"
}
# default
variable "mysql_disk_size" {
  description = "Disk size for MySQL cluster in GB"
  type        = number
  default     = 30
}
# default
variable "mysql_config" {
  description = "MySQL configuration"
  type = object({
    sql_mode                      = string
    max_connections               = number
    default_authentication_plugin = string
    innodb_print_all_deadlocks    = bool
  })
  default = {
    sql_mode                      = "ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
    max_connections               = 100
    default_authentication_plugin = "MYSQL_NATIVE_PASSWORD"
    innodb_print_all_deadlocks    = true
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
