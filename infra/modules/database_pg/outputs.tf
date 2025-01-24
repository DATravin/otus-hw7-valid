output "db_host_fqdn" {
  value = yandex_mdb_postgresql_cluster.cluster.host[0].fqdn
}
