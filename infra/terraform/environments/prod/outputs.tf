output "ip_publico" {
  value = module.compute.ip_publico
}

output "tunel_ssh" {
  value = "ssh -L 8080:localhost:8080 -L 5432:localhost:5432 ubuntu@${module.compute.ip_publico}"
}
