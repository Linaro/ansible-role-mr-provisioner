import requests
#from urlparse import urljoin
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urljoin

# curl -X POST "http://192.168.0.3:5000/api/v1/image"
# -H "accept: application/json"
# -H "Authorization: DEADBEEF"
# -H "content-type: multipart/form-data"
# -F "file=@linux;type="
# -F "q={ "description": "Example image",
#         "type": "Kernel",
#         "arch": "arm64",
#         "public": false,
#         "known_good": true } "
headers = {'Authorization': '/T9kmICCxhhk0Ec6kCqudgXwwWNTzNrrqmuCTCAwA2U='}
url = urljoin("http://192.168.0.3:5000", "/api/v1/image")
files = {'file': open('../../../builds/debian-staging/476/linux', 'rb')}
data = {'q': '{"name": "drue test 476", "description": "", "type": "Kernel", "arch": "arm64"}'
        }
r = requests.post(url, files=files, data=data, headers=headers)
if r.status_code != 200:
    print('Error posting {}, HTTP {}, {}'.format(url,
                     r.status_code, r.reason))
print(r.status_code)
print(r.json())
import pdb; pdb.set_trace()

