#! /bin/bash
command -v git >/dev/null 2>&1 ||
{ echo >&2 "Git is not installed. Installing..";
  apt install -y -qq git > /dev/null && echo "Git Installed"
}
command -v python3 >/dev/null 2>&1 ||
{ echo >&2 "Python is not installed. Installing..";
  apt install -y -qq python3 > /dev/null && echo "Python Installed"
}
unset TYPE
args=("$@")
for index in "${args[@]}" # Built with case for scalability, for when I add more argument options
do
    case $index in 
        "-t"|"--type")
            TYPE="${args[((i+1))]}"
        ;;
    esac
    ((i++))
done

echo "This Script requires root permissions to run correctly, please enter your password here:"
sudo chmod 666 /var/run/docker.sock
git clone https://github.com/ANVSupport/Automatic-CoC
cp Automatic-CoC/apps.json /tmp/apps.json || exit 1
chmod +x Automatic-CoC/PermissionTester.sh
if [[ ! -z $TYPE ]]; then
	python3 Automatic-CoC/main.py --type "${TYPE}" && exit 0
else
	python3 Automatic-CoC/main.py && exit 0
fi
exit 1