# VM Always Free da Oracle Cloud (ARM Ampere A1: 4 OCPU / 24 GB, grátis sem prazo).
# Roda o docker compose com Kafka, PostgreSQL, Debezium e a aplicação.
terraform {
  required_version = ">= 1.6"
  required_providers {
    oci = { source = "oracle/oci", version = "~> 6.15" }
  }
}

provider "oci" {
  region = var.regiao
}

data "oci_identity_availability_domains" "ads" {
  compartment_id = var.compartment_id
}

data "oci_core_images" "ubuntu_arm" {
  compartment_id           = var.compartment_id
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "24.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

resource "oci_core_vcn" "comex" {
  compartment_id = var.compartment_id
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "comex-vcn"
}

resource "oci_core_internet_gateway" "comex" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.comex.id
}

resource "oci_core_route_table" "comex" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.comex.id
  route_rules {
    destination       = "0.0.0.0/0"
    network_entity_id = oci_core_internet_gateway.comex.id
  }
}

# Só SSH aberto, e só para o seu IP. Kafka UI e Postgres acessados por túnel SSH.
resource "oci_core_security_list" "comex" {
  compartment_id = var.compartment_id
  vcn_id         = oci_core_vcn.comex.id
  egress_security_rules {
    destination = "0.0.0.0/0"
    protocol    = "all"
  }
  ingress_security_rules {
    source   = var.meu_ip_cidr
    protocol = "6"
    tcp_options {
      min = 22
      max = 22
    }
  }
}

resource "oci_core_subnet" "comex" {
  compartment_id    = var.compartment_id
  vcn_id            = oci_core_vcn.comex.id
  cidr_block        = "10.0.1.0/24"
  route_table_id    = oci_core_route_table.comex.id
  security_list_ids = [oci_core_security_list.comex.id]
}

resource "oci_core_instance" "comex" {
  compartment_id      = var.compartment_id
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "comex-plataforma"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4
    memory_in_gbs = 24
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu_arm.images[0].id
    boot_volume_size_in_gbs = 100
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.comex.id
    assign_public_ip = true
  }

  metadata = {
    ssh_authorized_keys = file(var.chave_ssh_publica)
    user_data           = base64encode(file("${path.module}/cloud-init.yaml"))
  }
}
