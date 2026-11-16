variable "regiao" {
  type    = string
  default = "sa-saopaulo-1"
}

variable "compartment_id" {
  type        = string
  description = "OCID do compartment (o tenancy serve na conta gratuita)"
}

variable "meu_ip_cidr" {
  type        = string
  description = "Seu IP público para liberar o SSH, ex.: 200.1.2.3/32"
}

variable "chave_ssh_publica" {
  type    = string
  default = "~/.ssh/id_ed25519.pub"
}
