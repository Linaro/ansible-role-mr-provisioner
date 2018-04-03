#!/usr/bin/python

import json
import requests

from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urljoin

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mr-provisioner-preseed

short_description: Manage preseed files in Mr. Provisioner

description:
    Implemented:
        - Upload new preseed
        - Discover existing preseeds by a given name.
    Not implemented:
        - modifying existing preseed
        - deleting existing preseed

options:
    name:
        description:
            - Name of the preseed
        required: true
    description:
        description:
            - Description of the preseed
        required: false
    path:
        description: Local file path to preseed file.
        required: true
    url:
        description: url to provisioner instance in the form of http://172.27.80.1:5000/
        required: true
    token:
        description: Mr. Provisioner auth token
        required: true
    known_good:
        description: Mark known good. Default false.
        required: false
    public:
        description: Mark public. Default false.
        required: false

author:
    - Jorge Niedbalski <jorge.niedbalski@linaro.org>
'''

EXAMPLES = '''
# Upload a preseed file to a MrProvisioner install.
- name: moonshot-generic-preseed
  path: ./preseeds/moonshot-generic.preseed.txt
  url: http://172.27.80.1:5000/
  token: "{{ provisioner_auth_token }}"
'''

RETURN = '''
  id: auto-assigned preseed id
  description: preseed description
  name: preseed name
  type: user defined type (default: preseed)
  user: User that owns the preseed
  known_good: true/false
  public: true/false
'''

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        description=dict(type='str', required=False, default=""),
        name=dict(type='str', required=True),
        type=dict(type='str', required=False, default="preseed"),
        path=dict(type='str', required=True),
        url=dict(type='str', required=True),
        token=dict(type='str', required=True),
        known_good=dict(type='bool', required=False, default=False),
        public=dict(type='bool', required=False, default=False),
    )

    result = dict(
        changed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    if module.check_mode:
        return result
    # Determine if image is already uploaded
    headers = {'Authorization': module.params['token']}
    url = urljoin(module.params['url'], "/api/v1/preseed?show_all=true")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        module.fail_json(msg='Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason), **result)
    for preseed in r.json():
        if preseed['name'] == module.params['name']:
            result['json'] = preseed
            module.exit_json(**result)

    headers = {'Authorization': module.params['token']}
    url = urljoin(module.params['url'], "/api/v1/preseed")

    with open(module.params['path'], 'r') as content:
        content = content.read()

    data = json.dumps({
        'description': module.params['description'],
        'type': module.params['type'],
        'name': module.params['name'],
        'known_good': module.params['known_good'],
        'public': module.params['public'],
        'content': content,
    })

    r = requests.post(url, data=data, headers=headers)
    if r.status_code != 201:
        msg = ("Error fetching {}, HTTP {} {}\nrequest data: {}\nresult json: {}".
                format(url, r.status_code, r.reason, data, r.json()))
        module.fail_json(msg=msg, **result)
    result['json'] = r.json()
    result['changed'] = True

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
