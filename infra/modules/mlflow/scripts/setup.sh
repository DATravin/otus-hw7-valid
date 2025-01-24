#!/bin/bash

# мое

# Функция для логирования
function log() {
    sep="----------------------------------------------------------"
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $sep " | tee -a $HOME/user_data_execution.log
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [INFO] $1" | tee -a $HOME/user_data_execution.log
}

# Устанавливаем yc CLI
log "Installing yc CLI"
export HOME="/home/ubuntu"
curl https://storage.yandexcloud.net/yandexcloud-yc/install.sh | bash

# Проверяем, что yc доступен
if command -v yc &> /dev/null; then
    log "yc CLI is now available"
    yc --version
else
    log "yc CLI is still not available. Adding it to PATH manually"
    export PATH="$PATH:$HOME/yandex-cloud/bin"
    yc --version
fi

# Устанавливаем библиотеки
log "Installing libs"
sudo apt-get update
sudo apt-get -y install python3-pip
sudo pip install mlflow
sudo pip install psycopg2-binary
sudo pip install boto3
sudo pip install s3cmd
sudo pip install pandas

# Устанавливаем переменные

log "add env variables"
echo "DB_USER=${postgresql_user_name}" >> /home/ubuntu/.bashrc
echo "DB_PASS=${postgresql_user_password}" >> /home/ubuntu/.bashrc
echo "DB_HOST=${db_host_fqdn}" >> /home/ubuntu/.bashrc
echo "DB_PORT=6432" >> /home/ubuntu/.bashrc
echo "DB_NAME=${postgresql_database_name}" >> /home/ubuntu/.bashrc
echo "S3_BUCKET=${s3_bucket_name}" >> /home/ubuntu/.bashrc
echo "MLFLOW_S3_ENDPOINT_URL=https://storage.yandexcloud.net/" >> /home/ubuntu/.bashrc

log "exports"
export HOME="/home/ubuntu"
# export DB_USER=${postgresql_user_name}
# export DB_PASS=${postgresql_user_password}
# export DB_HOST=${db_host_fqdn}
# export DB_PORT=6432
# export DB_NAME=${postgresql_database_name}
# export S3_BUCKET=${s3_bucket_name}
# export MLFLOW_S3_ENDPOINT_URL=https://storage.yandexcloud.net/


# Настраиваем s3cmd как прокинуть туда переменные?
log "Configuring s3cmd"
cat <<EOF > /home/ubuntu/.s3cfg
[default]
access_key = ${access_key}
secret_key = ${secret_key}
host_base = storage.yandexcloud.net
host_bucket = %(bucket)s.storage.yandexcloud.net
use_https = True
EOF

chown ubuntu:ubuntu /home/ubuntu/.s3cfg
chmod 600 /home/ubuntu/.s3cfg

# log "add cert"
# mkdir -p ~/.postgresql && \
# wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
#     --output-document ~/.postgresql/root.crt && \
# sudo chown ubuntu:ubuntu ~/.postgresql/root.crt && \
# chmod 0600 ~/.postgresql/root.crt


log "add cert"
mkdir -p ~/.postgresql && \
wget "https://storage.yandexcloud.net/cloud-certs/CA.pem" \
    --output-document ~/.postgresql/root.crt
sudo chown ubuntu:ubuntu ~/.postgresql/root.crt
chmod 0600 ~/.postgresql/root.crt


log "Setup completed successfully"
