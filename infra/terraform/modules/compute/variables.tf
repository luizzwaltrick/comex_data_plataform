variable "compartment_id" { type = string }
variable "nome" { type = string }
variable "subnet_id" { type = string }
variable "chave_ssh_publica" { type = string }

# Limites do Always Free: até 4 OCPU / 24 GB no total em A1 e 200 GB de disco.
variable "shape" {
  type    = string
  default = "VM.Standard.A1.Flex"
}

variable "ocpus" {
  type    = number
  default = 4
}

variable "memoria_gb" {
  type    = number
  default = 24
}

variable "disco_gb" {
  type    = number
  default = 100
}
