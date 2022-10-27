variable "subnet_id" {
  type    = string
  default = "subnet-08a246e70f57439e3"
}
variable "aws_region" {
  type    = string
  default = "us-east-1"
  }

variable "source_ami" {
  type    = string
  default = "ami-08c40ec9ead489470"
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

#Api
source "amazon-ebs" "my-ami" {
  region          = "${var.aws_region}"
  ami_name        = "csye6225_${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  ami_description = "AMI Assignment 4"
  ami_users       = ["868454036435", "483920429415"]
  ami_regions = [
    "us-east-1",
  ]

#instance
  instance_type = "t2.micro"
  source_ami    = "${var.source_ami}"
  ssh_username  = "${var.ssh_username}"
  subnet_id     = "${var.subnet_id}"

  launch_block_device_mappings {
    delete_on_termination = true
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
  }
}

build {
  sources = ["source.amazon-ebs.my-ami"]
  provisioner "file" {
    source      = "app.tar.gz"
    destination = "/home/ubuntu/app.tar.gz"
  }
  provisioner "shell" {
    environment_vars = [
      "DEBIAN_FRONTEND=noninteractive",
      "CHECKPOINT_DISABLE=1"
    ]
    inline = [
      "sudo apt-get update",
      "sudo apt-get upgrade -y",
      "sudo apt install python3",
      "sudo apt-get update",
      "sudo apt-get install python3-mysql.connector -y",
      "sudo apt-get install python3-bcrypt -y",
      "sudo apt-get install python3-flask -y",
      "sudo apt-get install python3-pymysql -y",
      "sudo apt-get install python3-sqlalchemy -y",
      "sudo apt install python3-dotenv -y",
      "sudo apt install python3-boto3 -y",
      "tar -xvf app.tar.gz",
      "sudo mv app.service /lib/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable app.service",
      "sudo systemctl start app.service",
    ]
  }

}
