Mr. Provisioner
===============

Provision a host using [Mr. Provisioner](https://github.com/mr-provisioner/mr-provisioner).

This role will upload a kernel and initrd file to Mr. Provisioner, then
configure the machine (based on inventory_hostname) to use the given kernel,
initrd, and preseed file. Then, it will do a PXE reboot and wait for the host
to come online.

Role Variables
--------------

``mr_provisioner_do_provision``: Defaults to True. Disable to skip all role
tasks. This is useful if all you want is the modules.

If mr_provisioner_do_provision is set, all of the following variables are
required:
- ``mr_provisioner_machine_name``: Machine's name.
- ``mr_provisioner_kernel_description``: Unique kernel description to use in
  provisioner.
- ``mr_provisioner_initrd_description``: Unique initrd description to use in
  provisioner.
- ``mr_provisioner_kernel_path``: Local path to kernel file for uploading to
  provisioner.
- ``mr_provisioner_initrd_path``: Local path to initrd file for uploading to
  provisioner.
- ``mr_provisioner_url``: Mr. Provisioner URL in the form of i.e.
  'http://192.168.0.3:5000'
- ``mr_provisioner_auth_token``: Auth token from Mr. Provisioner.
- ``mr_provisioner_arch``: Image architecture.
- ``mr_provisioner_subarch``: Machine subarchitecture.

Usage
-----

    - hosts: provision_this_machine
      vars:
        mr_provisioner_machine_name: "if you don't assign it, it will use inventory hostname"
        mr_provisioner_kernel_description: "debian-installer staging build 495"
        mr_provisioner_initrd_description: "debian-installer staging build 495"
        mr_provisioner_kernel_path: "./builds/debian-staging/495/linux"
        mr_provisioner_initrd_path: "./builds/debian-staging/495/initrd.gz"
        mr_provisioner_url: "http://192.168.0.3:5000"
        mr_provisioner_auth_token: "MYSUPERFANCYTOKENFROMPROVISIONER"
        mr_provisioner_preseed_name: "danrue/erp-17.08-debian-20170727.567664d4"
        mr_provisioner_preseed_path: "./preseeds/erp-17.08-generic"
        mr_provisioner_arch: "arm64"
        mr_provisioner_subarch: "efi"
      roles:
        - role: Linaro.mr-provisioner

    - hosts: mr_provisoner_hosts
      tasks:
        - name: Wait for host for 3600 seconds, but only start checking after 60.
          wait_for_connection:
            delay: 60
            timeout: 3600

Role Modules
------------

This role contains four ansible modules:
- ``mr_provisioner_image``: Handles uploading image files to Mr. Provisioner.
- ``mr_provisioner_machine_provision``: Handles provisioning a host in Mr.
  Provisioner.
- ``mr_provisioner_preseed``: Handles uploading preseed files to Mr. Provisioner.
- ``mr_provisioner_get_ip``: Handles fetching the provisioned machine's IP from Mr. Provisioner.

By default, these modules are used by the tasks in the role. They may also be
used outside the role if the included role tasks are not suitable.

    - hosts: all
      roles:
        - role: Linaro.mr-provisioner
          mr_provisioner_do_provision: False

By setting mr_provisioner_do_provision to False, the modules will be made
available but no tasks will run.

Caveats
-------

Most of these behaviors can be fixed but in the meantime, FYI!

- Use unique image descriptions. The kernel and initrd files are only uploaded
  once. If they're changed locally but the description is the same, they will
  not be re-uploaded. If it finds someone else's image with the same
  description, it will use it. If there are multiple images with the same
  description, it will use the first one found (non deterministically).

See Also
--------

Role to retrieve a kernel and initrd file from Linaro's ERP:
[erp-get-build](https://galaxy.ansible.com/Linaro/erp-get-build/)

License
-------

BSD

Author Information
------------------

Dan Rue <dan.rue@linaro.org>
