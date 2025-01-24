variable "instance_user" {
  description = "Name of the user to create on the compute instance"
  type        = string
}

variable "instance_name" {
  description = "Name of the compute instance"
  type        = string
}

variable "service_account_id" {
  description = "ID of the service account"
  type        = string
}

variable "subnet_id" {
  description = "ID of the subnet"
  type        = string
}

variable "ubuntu_image_id" {
  description = "ID of the Ubuntu image"
  type        = string
}

variable "public_key_path" {
  description = "Path to the public SSH key"
  type        = string
}

variable "private_key_path" {
  description = "Path to the private SSH key"
  type        = string
}

variable "provider_config" {
  description = "Yandex Cloud configuration"
  type = object({
    zone      = string
    folder_id = string
    token     = string
    cloud_id  = string
  })
}

# new
variable "postgresql_database_name" {
  type = string
}

variable "postgresql_user_name" {
  type = string
}

variable "postgresql_user_password" {
  type = string
}

variable "access_key" {
  description = "Access key for the bucket"
  type        = string
}

variable "secret_key" {
  description = "Secret key for the bucket"
  type        = string
}

variable "db_host_fqdn" {
  description = "bd host "
  type        = string
}

variable "s3_bucket_name" {
  description = "name of bucket s3 "
  type        = string
}
