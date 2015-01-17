#! /bin/bash

Check_package()
{
	PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $1|grep "install ok installed")
	echo "Checking for $1..."
	if [ "" = "$PKG_OK" ]; then
	  echo "[CHECK] No $1. Install $1 before running this script."
	  exit 0
	fi
	echo "[CHECK] ok."
}

echo "**********************************"
echo "* Cloudinion installation script *"
echo "**********************************\n"
echo "[INFO] Performing checks..."

Check_package "python-pip"
Check_package "sudo"

echo "[INFO] Checks performed successfully\n"

echo "[INFO] Installing pip and virtual environments"
sudo pip install -U pip
sudo pip install -U virtualenvwrapper
mkdir ~/.virtualenvs
echo "[INFO] Done\n"

echo "[INFO] Modifying .bashrc file..." 
echo "" >> ~/.bashrc
echo "# Cloudinion" >> ~/.bashrc
echo "export WORKON_HOME=\"$HOME/.virtualenvs\"" >> ~/.bashrc
echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
echo "" >> ~/.bashrc
#echo "\n# Cloudinion\nexport WORKON_HOME=\"$HOME/.virtualenvs\"\nsource /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
#. ~/.bashrc --source-only
echo "[INFO] Done\n"

echo "[INFO] Installing Django"
. /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv --distribute django1.7
sudo pip install -r django-server/requirements.txt
echo "[INFO] Done\n"

echo "[INFO] Installing Flask"
workon django1.7
sudo pip install https://github.com/mitsuhiko/flask/tarball/master
echo "[INFO] Done\n"

