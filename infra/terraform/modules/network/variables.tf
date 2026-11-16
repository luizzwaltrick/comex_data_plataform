variable "compartment_id" { type = string }
variable "nome" { type = string }
variable "ssh_cidr" { type = string }

variable "cidr_vcn" {
  type    = string
  default = "10.0.0.0/16"
}
