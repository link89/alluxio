#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os

import yaml

from util import mkdir_p


def create_inventory_id_and_tags(ec2_conf, ec2_info):
    # mock the inventory and ids that should be generated by vagrant
    inventory_dir = '.vagrant/provisioners/ansible/inventory'
    mkdir_p(inventory_dir)
    inventory = open(os.path.join(inventory_dir, 'vagrant_ansible_inventory'), 'w')

    machine_dir = '.vagrant/machines'
    mkdir_p(machine_dir)

    tag = ec2_conf['Tag']
    tags = {}
    for i, instance in enumerate(ec2_info['instances']):
        host = "TachyonMaster" if i == 0 else "TachyonWorker{id}".format(id=i)
        inventory.write("{host} ansible_ssh_host={ip} ansible_ssh_port=22\n".format(host=host, ip=instance['public_ip']))

        instance_id = str(instance['id'])
        id_dir = os.path.join(machine_dir, host, 'aws')
        mkdir_p(id_dir)
        with open(os.path.join(id_dir, 'id'), 'w') as f:
            f.write(instance_id)

        tags[instance_id] = '{tag}-{host}'.format(tag=tag, host=host)

    inventory.close()

    # map instance id to its tag
    spot_tag_dir = 'spot/roles/tag_ec2/vars'
    mkdir_p(spot_tag_dir)
    tag_vars = open(os.path.join(spot_tag_dir, 'main.yml'), 'w')
    var = {
        "tags": tags,
        "region": ec2_conf["Region"],
    }
    yaml.dump(var, tag_vars, default_flow_style=False)
    tag_vars.close()


if __name__ == '__main__':
    temp_folder = yaml.load(open('spot/roles/create_ec2/vars/main.yml'))['temp_folder']
    ec2_info = json.load(open(os.path.join(temp_folder, 'ec2.info')))
    ec2_conf = yaml.load(open('conf/ec2.yml'))
    create_inventory_id_and_tags(ec2_conf, ec2_info)
