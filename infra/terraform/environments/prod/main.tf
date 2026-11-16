terraform {
  required_version = ">= 1.6"
  required_providers {
    oci = { source = "oracle/oci", version = "~> 6.15" }
  }
}

provider "oci" {
  region = var.regiao
}

module "network" {
  source         = "../../modules/network"
  compartment_id = var.compartment_id
  nome           = "comex"
  ssh_cidr       = var.meu_ip_cidr
}

module "compute" {
  source            = "../../modules/compute"
  compartment_id    = var.compartment_id
  nome              = "comex-plataforma"
  subnet_id         = module.network.subnet_id
  chave_ssh_publica = file(var.chave_ssh_publica)
}
