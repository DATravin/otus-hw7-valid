variable "yc_instance_user" {
  type = string
}

variable "yc_instance_name" {
  type = string
}

variable "yc_instance_mlflow_name" {
  type = string
}

variable "yc_network_name" {
  type = string
}

variable "yc_subnet_name" {
  type = string
}

variable "yc_service_account_name" {
  type    = string
}

variable "yc_bucket_name" {
  type = string
}

variable "yc_cold_bucket_name" {
  type = string
}

variable "yc_storage_endpoint_url" {
  type = string
  default = "https://storage.yandexcloud.net"
}

variable "ubuntu_image_id" {
  type    = string
}

variable "ubuntu_image_mlflow_id" {
  type    = string
}

variable "public_key_path" {
  type = string
}

variable "private_key_path" {
  type = string
}

variable "yc_config" {
  type = object({
    zone      = string
    folder_id = string
    token     = string
    cloud_id  = string
  })
  description = "Yandex Cloud configuration"
}

variable "airflow_db_conn_default" {
  type = string
}

variable "yc_mysql_cluster_name" {
  type = string
}

variable "yc_mysql_version" {
  type = string
}

variable "yc_mysql_environment" {
  type = string
}

variable "mysql_database_name" {
  type = string
}

variable "mysql_user_name" {
  type = string
}

variable "mysql_user_password" {
  type = string
}

variable "yc_postgresql_cluster_name" {
  type = string
}

variable "yc_postgresql_version" {
  type = string
}

variable "yc_postgresql_environment" {
  type = string
}

variable "postgresql_database_name" {
  type = string
}

variable "postgresql_user_name" {
  type = string
}

variable "postgresql_user_password" {
  type = string
}
