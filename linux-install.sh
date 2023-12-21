#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

set -e

echo -e "${CYAN}Установщик FunPayCardinal${NC}"

echo -e "${GREEN}Обновление пакетов...${NC}"
sudo apt update -y && sudo apt upgrade -y

echo -e "${GREEN}Установка языкового пакета...${NC}"
sudo apt install -y language-pack-ru

echo -e "${GREEN}Проверка локалей...${NC}"
if ! locale -a | grep -q 'ru_RU.utf8'; then
    echo -e "${GREEN}Обновление локалей...${NC}"
    sudo update-locale LANG=ru_RU.utf8

    echo -e "${RED}Локали ещё не установлены. Пожалуйста, перезапустите терминал и повторите команду запуска скрипта.${NC}"
    exit 1
fi

echo -e "${GREEN}Установка software-properties-common...${NC}"
sudo apt install -y software-properties-common

echo -e "${GREEN}Добавление репозитория deadsnakes/ppa...${NC}"
sudo add-apt-repository -y ppa:deadsnakes/ppa

echo -e "${GREEN}Переход в домашнюю директорию...${NC}"
cd ~

echo -e "${GREEN}Установка Python 3.11 и зависимостей...${NC}"
sudo apt install -y python3.11 python3.11-dev python3.11-gdbm python3.11-venv
wget https://bootstrap.pypa.io/get-pip.py -nc
sudo python3.11 get-pip.py

rm -rf get-pip.py

echo -e "${GREEN}Установка git...${NC}"
sudo apt install -y git

sudo rm -rf FunPayCardinal

echo -e "${GREEN}Клонирование репозитория FunPayCardinal...${NC}"
git clone https://github.com/sidor0912/FunPayCardinal

echo -e "${GREEN}Переход в директорию проекта...${NC}"
cd FunPayCardinal

echo -e "${GREEN}Установка зависимостей бота...${NC}"
sudo python3.11 setup.py

echo -e "${GREEN}Сейчас необходимо выполнить первичную установку${NC}"
sudo python3.11 main.py

echo -e "${GREEN}Ок, теперь добавим бота как фоновый процесс${NC}"

echo -e "${GREEN}Установка curl...${NC}"
sudo apt-get install -y curl

echo -e "${GREEN}Загрузка NodeJS...${NC}"
curl -sL https://deb.nodesource.com/setup_16.x | sudo bash -

echo -e "${GREEN}Установка NodeJS...${NC}"
sudo apt -y install nodejs

echo -e "${GREEN}Установка pm2...${NC}"
sudo npm install -g pm2

pm2 start main.py --interpreter=python3.11 --name=FunPayCardinal
pm2 save
pm2 startup

echo -e "\n${CYAN}Установка FunPayCardinal завершена!${NC}"
echo -e "${CYAN}Для просмотра логов используйте команду: pm2 logs FunPayCardinal${NC}"

pm2 logs FunPayCardinal