output "ip_publico" {
  value = oci_core_instance.comex.public_ip
}

output "tunel_ssh" {
  value = "ssh -L 8080:localhost:8080 -L 5432:localhost:5432 ubuntu@${oci_core_instance.comex.public_ip}"
}
