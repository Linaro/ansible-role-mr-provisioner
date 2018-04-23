#!/usr/bin/python

import json
import requests

from future.standard_library import install_aliases
install_aliases()

try:
    from urlparse import urljoin    #Python2
except ImportError:
    from urllib.parse import urljoin    #Python3

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: mr-provisioner-image

short_description: Manage machine images in Mr. Provisioner

description:
    Implemented:
        - Upload new image
        - Discover existing images matching a given description.
    Not implemented:
        - modifying existing image (such as known_good/public)
        - deleting existing image

options:
    description:
        description:
            - Name of the image
        required: true
    type:
        description:
            - Image type. May be 'Kernel' or 'Initrd'.
        required: true
    arch:
        description: Image architecture. e.g. arm64, x86_64
        required: true
    path:
        description: Local file path to image file.
        required: true
    url:
        description: url to provisioner instance in the form of http://192.168.0.3:5000/
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
    - Dan Rue <dan.rue@linaro.org>
'''

EXAMPLES = '''
# Upload a linux kernel image
- description: debian-installer staging build 471
  type: Kernel
  arch: arm64
  path: ./builds/staging/427/linux
  url: http://192.168.0.3:5000/
  token: "{{ provisioner_auth_token }}"
'''

RETURN = '''
  id: auto-assigned image id
  description: image description
  name: auto-assigned image name
  type: Kernel or Initrd
  upload_date: Date of upload
  user: User that owns the image
  known_good: true/false
  public: true/false
  arch: arm64
'''

from ansible.module_utils.basic import AnsibleModule

def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        description=dict(type='str', required=True),
        type=dict(type='str', required=True),
        arch=dict(type='str', required=True),
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

    allowed_types = ["Kernel", "Initrd"]
    if module.params['type'] not in allowed_types:
        module.fail_json(msg="error: type is '{}'; must be one of {}".format(
                         module.params['type'], allowed_types), **result)

    # Determine if image is already uploaded
    headers = {'Authorization': module.params['token']}
    url = urljoin(module.params['url'], "/api/v1/image?show_all=true")
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        module.fail_json(msg='Error fetching {}, HTTP {} {}'.format(url,
                         r.status_code, r.reason), **result)
    for image in r.json():
        if (image['description'] == module.params['description'] and
            image['type'] == module.params['type'] and
            image['arch'] == module.params['arch']):
                #XXX Not implemented: modify existing image
                result['json'] = image
                module.exit_json(**result)

    # Image does not yet exist. Upload it.
    # curl -X POST "http://192.168.0.3:5000/api/v1/image"
    # -H "accept: application/json"
    # -H "Authorization: DEADBEEF"
    # -H "content-type: multipart/form-data"
    # -F "file=@linux;type="
    # -F "q={ "description": "Example image",
    #         "type": "Kernel",
    #         "public": false,
    #         "known_good": true } "
    headers = {'Authorization': module.params['token']}
    url = urljoin(module.params['url'], "/api/v1/image")
    files = {'file': open(module.params['path'], 'rb')}
    data = {'q': json.dumps({
                 'description': module.params['description'],
                 'type': module.params['type'],
                 'arch': module.params['arch'],
                 'known_good': module.params['known_good'],
                 'public': module.params['public'],
             })
           }
    r = requests.post(url, files=files, data=data, headers=headers)
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
