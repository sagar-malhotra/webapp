variable "aws_region" {
  type    = string
  default = "us-east-1"
  }

variable "source_ami" {
  type    = string
  default = "ami-08c40ec9ead489470" # Ubuntu 22.04 LTS
}

variable "ssh_username" {
  type    = string
  default = "ubuntu"
}

variable "subnet_id" {
  type    = string
  default = "subnet-0145c1368e8cb555f"
}

# https://www.packer.io/plugins/builders/amazon/ebs
source "amazon-ebs" "my-ami" {
  region          = "${var.aws_region}"
  ami_name        = "csye6225_${formatdate("YYYY_MM_DD_hh_mm_ss", timestamp())}"
  ami_description = "AMI for CSYE 6225"
  ami_users       = ["126218098708", "501904329608"]
  ami_regions = [
    "us-east-1",
  ]


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
      "echo 'RAN 1'",

      "echo 'RAN 2'",
      "sudo apt-get update",
      "echo 'RAN 3'",
      "sudo apt-get upgrade -y",
      "echo 'RAN 4'",
      "echo 'RAN 9'",
      "sudo apt install python3",
      "echo 'RAN 10'",
      "sudo apt-get update",
      "sudo apt install mysql-server -y",
      "sudo mysqladmin -u root password 'password'",
      "echo 'RAN 11'",
      "sudo apt-get install python3-mysql.connector -y",
      "echo 'RAN 12'",
      "sudo apt-get install python3-bcrypt -y",
      "echo 'RAN 13'",
      "sudo apt-get install python3-flask -y",
      "echo 'RAN 14'",
      "sudo apt-get install python3-pymysql -y",
      "echo 'RAN 15'",
      "sudo apt-get install python3-sqlalchemy -y",
      "echo 'RAN 16'",
      "sudo systemctl start mysql.service",
      "sudo mysql -u root <<MYSQL_SCRIPT",
      "CREATE USER 'user'@'localhost' IDENTIFIED BY 'password';",
      "GRANT ALL PRIVILEGES ON *.* TO 'user'@'localhost';",
      "FLUSH PRIVILEGES;",
      "MYSQL_SCRIPT",
      "echo 'RAN 17'",
      "sudo ls",
      "echo 'RAN 18'",
      "sudo pwd",
      "echo 'RAN 19'",
      "tar -xvf app.tar.gz",
      "sudo mv app.service /lib/systemd/system/",
      "sudo systemctl daemon-reload",
      "sudo systemctl enable app.service",
      "sudo systemctl start app.service",
    ]
  }

}
