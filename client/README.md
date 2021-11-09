# Installation procedure
This procedure describe how to get a development environment ready.
No matter your system we assume you have python 3 installed on your system.
On Windows don't forget to add python/pip in your PATH environment variable if you didn't let the installer wizzard do it for you.


## Raspberry(Raspbian)
- Install swig (**sudo apt install swig** on debian like, **sudo pacman -S swig** on Arch)
- Install pyqt5 dev environment **sudo apt-get install pyqt5-dev**
- Install smart card daemon **sudo apt install pcscd**
- Install smart card library (**sudo apt install libpcsclite-dev**)
- You must force the daemon to not sleep if reader is inactive, find pcscd.service on your system **sudo find / -name "pcscd.service"** or look in `/usr/lib/systemd/system/pcscd.service`
- Remove **--auto-exit** from **ExecStart=/usr/bin/pcscd --foreground --auto-exit**
- Restart your machine
- clone the repository
- Create a virtual environment with system package (**virtualenv --system-site-packages venv**)


## Linux systems
- Install swig (**sudo apt install swig** on debian like, **sudo pacman -S swig** on Arch)
- Install smart card library and daemon (**sudo apt install libpcsclite-dev && sudo apt install pcscd** on debian like, **sudo pacman -S ccid** on Arch)
- You must force the daemon to not sleep if reader is inactive, find pcscd.service on your system **sudo find / -name "pcscd.service"** or look in `/usr/lib/systemd/system/pcscd.service`
- Remove **--auto-exit** from **ExecStart=/usr/bin/pcscd --foreground --auto-exit**
- Restart your machine
- Clone the repository
- Create a virtual environment (**virtualenv venv**)
- Source the environment (**source ./venv/bin/activate**)
- Install dependencies (**pip install -r requirements.txt**)
- launch program (**./scripts/gmc**)



