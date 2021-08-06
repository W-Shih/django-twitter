# =================================================================================================
#                                  All Rights Reserved.
# =================================================================================================
# File description:
#       provision.sh to set up virtual machine env
#
# =================================================================================================
#    Date      Name                    Description of Change
# 02-Aug-2021  Wayne Shih              Initial create
# 05-Aug-2021  Wayne Shih              Create superuser
# $HISTORY$
# =================================================================================================

#!/usr/bin/env bash

echo 'Start!'

sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2

cd /vagrant

sudo apt-get update
sudo apt-get install tree

# 安装配置 mysql8
if ! [ -e /vagrant/mysql-apt-config_0.8.15-1_all.deb ]; then
	wget -c https://dev.mysql.com/get/mysql-apt-config_0.8.15-1_all.deb
fi

sudo dpkg -i mysql-apt-config_0.8.15-1_all.deb
sudo DEBIAN_FRONTEND=noninteractivate apt-get install -y mysql-server
sudo apt-get install -y libmysqlclient-dev

if [ ! -f "/usr/bin/pip" ]; then
  sudo apt-get install -y python3-pip
  sudo apt-get install -y python-setuptools
  sudo ln -s /usr/bin/pip3 /usr/bin/pip
else
  echo "pip3 已安装"
fi

# 升级 pip，目前存在问题，read timed out，看脸，有时候可以，但大多时候不行
# python -m pip install --upgrade pip
# 换源完美解决
# 安装pip所需依赖
pip install --upgrade setuptools      # -i https://pypi.tuna.tsinghua.edu.cn/simple # 清華鏡像
pip install --ignore-installed wrapt  # -i https://pypi.tuna.tsinghua.edu.cn/simple
# 安装 pip 最新版
pip install -U pip                    # -i https://pypi.tuna.tsinghua.edu.cn/simple
# 根据 requirements.txt 里的记录安装 pip package，确保所有版本之间的兼容性
pip install -r requirements.txt       # -i https://pypi.tuna.tsinghua.edu.cn/simple


# 设置 mysql 的 root 账户的密码为 yourpassword
# 创建名为 twitter 的数据库
sudo mysql -u root << EOF
	ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'yourpassword';
	flush privileges;
	show databases;
	CREATE DATABASE IF NOT EXISTS twitter;
EOF
# fi

# superuser 名字
USER="admin"
# superuser 密码
PASS="admin"
# superuser 邮箱
MAIL="admin@twitter.com"
script="
from django.contrib.auth.models import User;

username = '$USER';
password = '$PASS';
email = '$MAIL';

if not User.objects.filter(username=username).exists():
	User.objects.create_superuser(username, email, password);
	print( 'Superuser created.' );
else:
	print( 'Superuser creation skipped.' );
"
printf " $script"  | python manage.py shell


# 如果想直接进入 /vagrant 路径下
# 请输入 vagrant ssh 命令进入
# 手动输入
# 输入 ls -a
# 输入 vi .bashrc
# 在最下面，添加cd /vagrant

echo 'All Done!'
