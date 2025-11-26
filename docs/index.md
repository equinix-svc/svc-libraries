# SVC Python Libraries

A collection of internal Python libraries used by the SVC team for
network automation and system synchronization.  
This repository is organized as a *monorepo* and managed using **Poetry**.

## 📦 Available Packages

This repository contains three standalone libraries:

| Package | Description |
|--------|-------------|
| **svc_juniper_lib** | Helpers for interacting with Juniper devices |
| **svc_netbox_lib** | Utilities for interacting with NetBox (REST API wrappers, data fetchers). |
| **svc_synchronize_lib** | Higher-level sync logic combining Juniper + NetBox operations. |

Each library is published as an installable Python package.

---

## 🧱 Repository Structure
```
svc-libraries/
│
├── packages/
│ ├── svc_juniper_lib/
│ │ └── src/svc_juniper_lib/
│ │
│ ├── svc_netbox_lib/
│ │ └── src/svc_netbox_lib/

│ └── svc_synchronize_lib/
│ └── src/svc_synchronize_lib/
│
├── docs/ # MkDocs documentation (generated online)
├── mkdocs.yml # Documentation configuration
└── pyproject.toml # Monorepo workspace config
```
## 🚀 Installation

You can install any library *directly from GitHub*:

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

## Documentation

Full API documentation is available at:

https://equinix-svc.github.io/svc-libraries

Documentation is auto-generated using `mkdocs-material` + `mkdocstrings`.
Source files live under `docs/`.