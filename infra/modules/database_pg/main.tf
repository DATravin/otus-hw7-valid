# Основной файл конфигурации Terraform

# Создание сети и подсети

# resource "yandex_vpc_network" "network" {
#   name = var.yc_network_name
# }

# resource "yandex_vpc_subnet" "subnet" {
#   zone           = var.yc_zone
#   network_id     = yandex_vpc_network.network.id
#   v4_cidr_blocks = [var.yc_subnet_range]
# }

################################################################################

# Создание сервисного аккаунта
# resource "yandex_iam_service_account" "sa" {
#   name        = var.yc_service_account_name
#   description = "Service account for Dataproc cluster and related services"
# }

# Назначение ролей сервисному аккаунту
# resource "yandex_resourcemanager_folder_iam_member" "sa_roles" {
#   for_each = toset([
#     "storage.admin",
#     "storage.uploader",
#     "storage.viewer",
#     "storage.editor"
#   ])

#   folder_id = var.yc_folder_id
#   role      = each.key
#   member    = "serviceAccount:${yandex_iam_service_account.sa.id}"
# }

################################################################################

# Создание статического ключа доступа для сервисного аккаунта
# resource "yandex_iam_service_account_static_access_key" "sa-static-key" {
#   service_account_id = yandex_iam_service_account.sa.id
# }

#Запись ключей в .env и sa-keys.json
# resource "null_resource" "update_env_and_save_keys" {
#   provisioner "local-exec" {
#     command = <<EOT
#       # Определяем переменные для access_key и secret_key
#       ACCESS_KEY=${yandex_iam_service_account_static_access_key.sa-static-key.access_key}
#       SECRET_KEY=${yandex_iam_service_account_static_access_key.sa-static-key.secret_key}

#       # Замена пустых переменных в .env
#       # sed -i "s/^S3_ACCESS_KEY=.*/S3_ACCESS_KEY=$ACCESS_KEY/" ../.env
#       # sed -i "s/^S3_SECRET_KEY=.*/S3_SECRET_KEY=$SECRET_KEY/" ../.env
#     EOT
#   }

#   # Добавляем зависимости, чтобы эта команда выполнялась после создания ключей
#   depends_on = [
#     yandex_iam_service_account_static_access_key.sa-static-key
#   ]
# }

################################################################################

# Создание бакета
# генерация случайной id в названии для бакета. Передается ниже в имя бакета
# resource "random_id" "bucket_id" {
#   byte_length = 8
# }

# resource "yandex_storage_bucket" "bucket" {
#   bucket        = "${var.yc_bucket_name}-${random_id.bucket_id.hex}"
#   access_key    = yandex_iam_service_account_static_access_key.sa-static-key.access_key
#   secret_key    = yandex_iam_service_account_static_access_key.sa-static-key.secret_key
#   force_destroy = true
# }

# Storage ресурсы
# создаем бакет. Важно в конце Что мы можем убить бакет "силой"
# resource "yandex_storage_bucket" "bucket" {
#   bucket     = "${var.yc_bucket_name}-${var.yc_folder_id}"
#   access_key = yandex_iam_service_account_static_access_key.sa-static-key.access_key
#   secret_key = yandex_iam_service_account_static_access_key.sa-static-key.secret_key
#   force_destroy = true
# }

# resource "null_resource" "update_env_and_save_bucket_name" {
#   provisioner "local-exec" {
#     command = <<EOT
#       # Определяем переменную BUCKET_NAME с именем бакета
#       BUCKET_NAME=${yandex_storage_bucket.bucket.bucket}

#       # Замена переменной BUCKET_NAME в .env
#       # sed -i "s/^S3_BUCKET_NAME=.*/S3_BUCKET_NAME=$BUCKET_NAME/" ../.env
#     EOT
#   }

#   # Добавляем зависимости, чтобы эта команда выполнялась после создания ключей
#   depends_on = [
#     yandex_storage_bucket.bucket
#   ]
# }

################################################################################

# MySQL ресурсы
resource "yandex_mdb_postgresql_cluster" "cluster" {
  name        = var.yc_postgresql_cluster_name
  environment = var.yc_postgresql_environment
  network_id  = var.network_id


  config {

    version     = var.yc_postgresql_version

    resources {
      resource_preset_id = var.postgresql_resource_preset_id
      disk_type_id       = var.postgresql_disk_type_id
      disk_size          = var.postgresql_disk_size
    }

    postgresql_config = var.postgresql_config

  }

  maintenance_window {
    type = "ANYTIME"
  }

  host {
    zone      = var.yc_zone
    subnet_id = var.subnet_id
    assign_public_ip = true
  }
}



resource "yandex_mdb_postgresql_database" "db" {
  cluster_id = yandex_mdb_postgresql_cluster.cluster.id
  name       = var.postgresql_database_name
  owner      = var.postgresql_user_name
}

resource "yandex_mdb_postgresql_user" "user" {
  cluster_id = yandex_mdb_postgresql_cluster.cluster.id
  name       = var.postgresql_user_name
  password   = var.postgresql_user_password
  conn_limit = 50

  settings = {
    default_transaction_isolation = "read committed"
    log_min_duration_statement    = 5000
  }


}

# команда, чтобы автоматом сохранить некоторые константы для коннекта
# resource "null_resource" "update_env_with_db_host" {
#   provisioner "local-exec" {
#     command = <<EOT
#       # Определяем переменную DB_HOST с FQDN кластера
#       DB_HOST=${yandex_mdb_mysql_cluster.cluster.host[0].fqdn}

#       # Замена переменной DB_HOST в .env
#       #sed -i "s/^DB_HOST=.*/DB_HOST=$DB_HOST/" ../.env
#     EOT
#   }

#   # Указываем, что выполнение этого провиженера зависит от успешного создания кластера
#   depends_on = [
#     yandex_mdb_mysql_cluster.cluster
#   ]
# }
