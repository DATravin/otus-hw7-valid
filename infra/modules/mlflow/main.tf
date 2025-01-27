resource "yandex_compute_instance" "vm" {
  name               = var.instance_name
  service_account_id = var.service_account_id

  scheduling_policy {
    preemptible = true
  }

  resources {
    cores  = 2
    memory = 8
    core_fraction = 20 # 20% vCPU
  }

  boot_disk {
    initialize_params {
      image_id = var.ubuntu_image_id
      size     = 20
    }
  }

  network_interface {
    subnet_id = var.subnet_id
    nat       = true
  }

  metadata = {
    ssh-keys = "${var.instance_user}:${file(var.public_key_path)}"
    serial-port-enable = "1"
  }

  # metadata = {
  #   ssh-keys = "${var.instance_user}:${file(var.public_key_path)}"
  #   serial-port-enable = "1"

  #   user-data = templatefile("${path.module}/scripts/setup.sh", {
  #     postgresql_user_name     = var.postgresql_user_name
  #     postgresql_database_name = var.postgresql_database_name
  #     postgresql_user_password = var.postgresql_user_password
  #     db_host_fqdn             = var.db_host_fqdn
  #     private_key              = file(var.private_key_path)
  #     access_key               = var.access_key
  #     secret_key               = var.secret_key
  #     s3_bucket_name           = var.s3_bucket_name
  #   })
  # }



  connection {
    type        = "ssh"
    user        = var.instance_user
    private_key = file(var.private_key_path)
    host        = self.network_interface.0.nat_ip_address
  }

  # provisioner "file" {
  #   source      = "${path.module}/scripts/setup.sh"
  #   destination = "/home/${var.instance_user}/setup.sh"
  # }

  provisioner "file" {
    content = templatefile("${path.module}/scripts/setup.sh", {
      postgresql_user_name     = var.postgresql_user_name
      postgresql_database_name = var.postgresql_database_name
      postgresql_user_password = var.postgresql_user_password
      db_host_fqdn             = var.db_host_fqdn
      private_key              = file(var.private_key_path)
      access_key               = var.access_key
      secret_key               = var.secret_key
      s3_bucket_name           = var.s3_bucket_name
      }
    )
    destination = "/home/${var.instance_user}/setup.sh"
  }

  provisioner "remote-exec" {
    inline = [
      "chmod +x /home/${var.instance_user}/setup.sh",
      # "sudo /home/${var.instance_user}/setup.sh"
    ]
  }

}
