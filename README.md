# Installing SVC Python Libraries

### Install NetBox lib
```
pip install "git+https://git@github.com/equinix-svc/svc-libraries.git#subdirectory=packages/svc_netbox_lib"
```

### Install Juniper lib
```
pip install "git+https://git@github.com/equinix-sv/svc-libraries.git#subdirectory=packages/svc_juniper_lib"
```

### Install Synchronize lib
```
pip install "git+https://git@github.com/equinix-sv/svc-libraries.git#subdirectory=packages/svc_synchronize_lib"
```

### Usage
```python
from svc_netbox_lib.netbox import X
from svc_juniper_lib.juniper import Y
from svc_synchronize_lib.synchronize import Z
```