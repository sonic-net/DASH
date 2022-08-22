## Prepare Testbed Server

- Install Ubuntu[^1] 20.04 x64 on the server. (ubuntu-20.04.1-live-server-amd64.iso)
- Install Ubuntu prerequisites
    ```
    sudo apt -y update
    sudo apt -y upgrade
    sudo apt -y install \
      python3 \
      python3-pip \
      net-tools \
      curl \
      git \
      make
    sudo apt -y install ubuntu-desktop (TODO: remove this depedency)
    ```
- install Docker (all credits to https://docs.docker.com/engine/install/ubuntu/ )
    ```
    sudo apt-get remove docker docker-engine docker.io containerd runc
    sudo apt-get update
    sudo apt-get install \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg-agent \
      software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo apt-key fingerprint 0EBFCD88
    sudo add-apt-repository \
      "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) \
      stable"
    sudo apt-get update
    sudo apt-get install docker-ce docker-ce-cli containerd.io
    sudo docker run hello-world
    ```
    - add your user to docker group
        ```
        sudo usermod -aG docker $USER
        ```
 - install KVM
    ```
    sudo apt install cpu-checker
    sudo kvm-ok
    sudo apt -y install qemu-kvm libvirt-daemon-system libvirt-clients bridge-utils virtinst virt-manager libosinfo-bin
    sudo usermod -aG libvirt $USER
    sudo usermod -aG kvm $USER
    sudo systemctl enable libvirtd
    sudo systemctl start libvirtd
    ```
 
 - enable root (optional)
    ```
    sudo apt -y install mc
    (edit)/etc/ssh/sshd_config PermitRootLogin yes
    sudo passwd
    # we can use 'dash' as the default password
    sudo systemctl restart sshd
    ```
- setup management port configuration using this sample `/etc/netplan/00-installer-config.yaml`:
    ```
    network:
      version: 2
      ethernets:
        ens160:
          dhcp4: false
          dhcp6: false
      bridges:
        br1:
          interfaces: [ens160]
          addresses: [10.36.76.160/22]
          gateway4: 10.36.76.1
          mtu: 1500
          nameservers:
            addresses: [4.4.4.4, 8.8.8.8]
          parameters:
            stp: false
            forward-delay: 0
            max-age: 0
          dhcp4: no
          dhcp6: no
    ```
- reboot
    - ensure networking is ok
    - this is needed also for the permissions to be update, otherwise next step will fail

- clone the `DASH` repository into your working directory:
    ```
    git clone https://github.com/Azure/DASH
    ```

- build container
```
docker build --no-cache --tag dash/keysight:latest ./DASH/test/environments/keysight
docker tag dash/keysight:latest dash/keysight:1.0.0
```

- VMs
    - create vms folder 
    ```
    mkdir /vms
    chmod 775 -R /vms
    ```
    - download [IxNetwork kvm image](https://downloads.ixiacom.com/support/downloads_and_updates/eb/HF001150/IxNetworkWeb_KVM_9.20.2114.1.qcow2.tar.bz2).
    - copy `IxNetworkWeb_KVM_9.20.2112.27.qcow2.tar.bz2` to `/vms/` on your testbed server.


    - download [IxLoad kvm installer](https://downloads.ixiacom.com/support/downloads_and_updates/public/ixload/9.20/IxLoad_Web_9.20_KVM.sh)
    - copy `IxLoad_Web_9.20_KVM.sh` to `/vms/` on your testbed server.

    
- start the VMs:
    ```
    cd /vms
    
    tar xjf IxNetworkWeb_KVM_9.20.2114.1.qcow2.tar.bz2
    ./IxLoad_Web_9.20_KVM.sh -z -e Y
    
    virt-install --name IxNetwork-920 --memory 16000 --vcpus 8 --disk /vms/IxNetworkWeb_KVM_9.20.2112.27.qcow2,bus=sata --import --os-variant centos7.0 --network bridge=br1,model=virtio --noautoconsole
    virsh autostart IxNetwork-920
    
    virt-install --name IxLoad-920 --memory 16000 --vcpus 8 --disk /vms/9.20.0.279_ixload/IxLoad_Web_9.20_KVM.qcow2,bus=sata --import --os-variant ubuntu20.04 --network bridge=br1,model=virtio
    virsh autostart IxLoad-920
    ```

[^1]: it can be also centos archlinux .... but the example commands shown are for ubuntu
