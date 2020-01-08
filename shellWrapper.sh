#! /bin/bash
command -v git >/dev/null 2>&1 ||
{ echo >&2 "Git is not installed. Installing..";
  apt install -y -qq git > /dev/null && echo "Git Installed"
}
command -v python3 >/dev/null 2>&1 ||
{ echo >&2 "Python is not installed. Installing..";
  apt install -y -qq python3 > /dev/null && echo "Python Installed"
}
git clone https://github.com/ANVSupport/Automatic-CoC
cp Automatic-CoC/apps.json /tmp/apps.json
python3 Automatic-CoC/main.py && exit 0
exit 1