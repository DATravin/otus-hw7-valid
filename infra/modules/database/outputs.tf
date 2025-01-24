output "db_host_fqdn" {
  value = yandex_mdb_mysql_cluster.cluster.host[0].fqdn
}
