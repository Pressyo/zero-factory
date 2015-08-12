# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "1310Daily"

  config.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/saucy/current/saucy-server-cloudimg-amd64-vagrant-disk1.box"

  # config.vm.network :forwarded_port, guest: 80, host: 8080

  # Adiditional port forwarding, should you wish
  config.vm.network :forwarded_port, guest: 1234, host: 1234

  # DOWNLOAD MORE RAM!
  config.vm.provider "virtualbox" do |v|
    v.memory = 1024
  end

  # simple provisioning script
  config.vm.provision :shell, :path => "deploy/initialize.sh", :args => "'-v'"

end
