#!/bin/bash
commands='22'

RED='\033[1;91m'
CYAN='\033[1;96m'
PURPLE_LIGHT='\033[5;35m'
RESET='\033[0m'

start_process_line="${PURPLE_LIGHT}################################################################################"
end_process_line="################################################################################${RESET}"

logo="\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m\"\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52m,\e[0m\e[38;5;52mi\e[0m\e[38;5;88m>\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52m,\e[0m\e[38;5;88m>\e[0m\e[38;5;9m1\e[0m\e[38;5;160m[\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m^\e[0m\e[38;5;52m:\e[0m\e[38;5;124m?\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;0m^\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52mI\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;52m:\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52m,\e[0m\e[38;5;160m[\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;52mi\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0ml\e[0m\e[38;5;60mt\e[0m\e[38;5;60m/\e[0m\e[38;5;60mt\e[0m\e[38;5;60m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;17m!\e[0m\e[38;5;0m \e[0m\e[38;5;59m-\e[0m\e[38;5;60mt\e[0m\e[38;5;60m/\e[0m\e[38;5;60mt\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m/\e[0m\e[38;5;59m|\e[0m\e[38;5;59m[\e[0m\e[38;5;17mi\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0ml\e[0m\e[38;5;59m}\e[0m\e[38;5;60mf\e[0m\e[38;5;102mn\e[0m\e[38;5;102mn\e[0m\e[38;5;60mt\e[0m\e[38;5;59m}\e[0m\e[38;5;17m!\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52mI\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;160m]\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m1\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;59m/\e[0m\e[38;5;0m \e[0m\e[38;5;145mL\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;188ma\e[0m\e[38;5;59m|\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;59m{\e[0m\e[38;5;146mq\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;59m-\e[0m\e[38;5;0m \e[0m\e[38;5;0m\`\e[0m\e[38;5;9m1\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m1\e[0m\e[38;5;9m)\e[0m\e[38;5;9m)\e[0m\e[38;5;160m[\e[0m\e[38;5;167m(\e[0m\e[38;5;168mc\e[0m\e[38;5;0m\"\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m@\e[0m\e[38;5;15mB\e[0m\e[38;5;15m@\e[0m\e[38;5;188mM\e[0m\e[38;5;145mq\e[0m\e[38;5;146mp\e[0m\e[38;5;146mq\e[0m\e[38;5;146mq\e[0m\e[38;5;145mq\e[0m\e[38;5;146mq\e[0m\e[38;5;59m]\e[0m\e[38;5;0m \e[0m\e[38;5;102mY\e[0m\e[38;5;15m@\e[0m\e[38;5;15mB\e[0m\e[38;5;15m@\e[0m\e[38;5;188mb\e[0m\e[38;5;145mO\e[0m\e[38;5;145mZ\e[0m\e[38;5;188md\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;59m)\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;103mY\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;188m#\e[0m\e[38;5;188ma\e[0m\e[38;5;188m*\e[0m\e[38;5;15m%\e[0m\e[38;5;15m$\e[0m\e[38;5;59m{\e[0m\e[38;5;0m \e[0m\e[38;5;52ml\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;160m[\e[0m\e[38;5;95m{\e[0m\e[38;5;124m]\e[0m\e[38;5;132mu\e[0m\e[38;5;188ma\e[0m\e[38;5;195m&\e[0m\e[38;5;182mb\e[0m\e[38;5;0m,\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;102mX\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;102mX\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;59m?\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;59m/\e[0m\e[38;5;15m$\e[0m\e[38;5;15mB\e[0m\e[38;5;15m@\e[0m\e[38;5;145mm\e[0m\e[38;5;0m \e[0m\e[38;5;60mt\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;109mU\e[0m\e[38;5;17mi\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0mI\e[0m\e[38;5;59m\\e[0m\e[38;5;17m!\e[0m\e[38;5;0m \e[0m\e[38;5;124m-\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m1\e[0m\e[38;5;125m}\e[0m\e[38;5;95mt\e[0m\e[38;5;188mo\e[0m\e[38;5;224mW\e[0m\e[38;5;203mu\e[0m\e[38;5;9m1\e[0m\e[38;5;160m{\e[0m\e[38;5;124m-\e[0m\e[38;5;52mi\e[0m\e[38;5;0m\"\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;188m*\e[0m\e[38;5;145mC\e[0m\e[38;5;145mL\e[0m\e[38;5;145mC\e[0m\e[38;5;145mC\e[0m\e[38;5;145mC\e[0m\e[38;5;102mj\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;102mY\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;102mx\e[0m\e[38;5;59m~\e[0m\e[38;5;59m_\e[0m\e[38;5;59m]\e[0m\e[38;5;145mZ\e[0m\e[38;5;15m@\e[0m\e[38;5;15mB\e[0m\e[38;5;15m$\e[0m\e[38;5;103mY\e[0m\e[38;5;0m \e[0m\e[38;5;188mh\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;145mQ\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;52m,\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;160m[\e[0m\e[38;5;188ma\e[0m\e[38;5;15m$\e[0m\e[38;5;210mJ\e[0m\e[38;5;9m]\e[0m\e[38;5;9m)\e[0m\e[38;5;9m)\e[0m\e[38;5;160m[\e[0m\e[38;5;124m-\e[0m\e[38;5;52m!\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;188ma\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;102mY\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;188mh\e[0m\e[38;5;0m:\e[0m\e[38;5;0m.\e[0m\e[38;5;188m*\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;66mf\e[0m\e[38;5;0m \e[0m\e[38;5;0m\`\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m^\e[0m\e[38;5;160m}\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;160m]\e[0m\e[38;5;145mO\e[0m\e[38;5;15m$\e[0m\e[38;5;188mk\e[0m\e[38;5;210mC\e[0m\e[38;5;131m(\e[0m\e[38;5;88m>\e[0m\e[38;5;52ml\e[0m\e[38;5;52m,\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;188mh\e[0m\e[38;5;102mv\e[0m\e[38;5;102mc\e[0m\e[38;5;102mc\e[0m\e[38;5;102mv\e[0m\e[38;5;102mc\e[0m\e[38;5;59m\\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;102mY\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;15m&\e[0m\e[38;5;188mM\e[0m\e[38;5;188mM\e[0m\e[38;5;188mo\e[0m\e[38;5;188md\e[0m\e[38;5;145mC\e[0m\e[38;5;59m(\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;145mm\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;188mo\e[0m\e[38;5;0mI\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m^\e[0m\e[38;5;88m>\e[0m\e[38;5;160m}\e[0m\e[38;5;9m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;9m1\e[0m\e[38;5;9m)\e[0m\e[38;5;124m]\e[0m\e[38;5;152mp\e[0m\e[38;5;15m@\e[0m\e[38;5;195m&\e[0m\e[38;5;195mB\e[0m\e[38;5;66mu\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m}\e[0m\e[38;5;15m$\e[0m\e[38;5;15mB\e[0m\e[38;5;15m$\e[0m\e[38;5;102mX\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;102mX\e[0m\e[38;5;15m$\e[0m\e[38;5;15mB\e[0m\e[38;5;15m$\e[0m\e[38;5;59m)\e[0m\e[38;5;0m'\e[0m\e[38;5;0m^\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m~\e[0m\e[38;5;15mB\e[0m\e[38;5;15m$\e[0m\e[38;5;15m@\e[0m\e[38;5;15m$\e[0m\e[38;5;15m%\e[0m\e[38;5;145m0\e[0m\e[38;5;102mx\e[0m\e[38;5;59m_\e[0m\e[38;5;88m~\e[0m\e[38;5;160m{\e[0m\e[38;5;9m)\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;9m1\e[0m\e[38;5;9m(\e[0m\e[38;5;160m1\e[0m\e[38;5;167m)\e[0m\e[38;5;131m|\e[0m\e[38;5;131mf\e[0m\e[38;5;167mx\e[0m\e[38;5;52m<\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;59m{\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;145mL\e[0m\e[38;5;0m \e[0m\e[38;5;0m\`\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m \e[0m\e[38;5;109mU\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;59m1\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;59m+\e[0m\e[38;5;188mk\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;15m$\e[0m\e[38;5;224m*\e[0m\e[38;5;203mX\e[0m\e[38;5;9m(\e[0m\e[38;5;9m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m}\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m1\e[0m\e[38;5;9m1\e[0m\e[38;5;9m{\e[0m\e[38;5;9m}\e[0m\e[38;5;52m:\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;59m-\e[0m\e[38;5;188mh\e[0m\e[38;5;188mb\e[0m\e[38;5;188mh\e[0m\e[38;5;102mn\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;102mr\e[0m\e[38;5;188mh\e[0m\e[38;5;188mb\e[0m\e[38;5;188mh\e[0m\e[38;5;59m]\e[0m\e[38;5;0m \e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;59m]\e[0m\e[38;5;174mL\e[0m\e[38;5;203mv\e[0m\e[38;5;160m]\e[0m\e[38;5;160m]\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m[\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;88m<\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m^\e[0m\e[38;5;88mi\e[0m\e[38;5;160m?\e[0m\e[38;5;160m[\e[0m\e[38;5;160m1\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m[\e[0m\e[38;5;160m}\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m)\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;160m]\e[0m\e[38;5;52ml\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;52mi\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;160m1\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m[\e[0m\e[38;5;160m[\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;160m}\e[0m\e[38;5;88m~\e[0m\e[38;5;52m;\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;52m,\e[0m\e[38;5;124m]\e[0m\e[38;5;9m)\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m[\e[0m\e[38;5;160m]\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;160m}\e[0m\e[38;5;88m+\e[0m\e[38;5;52m;\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;88m>\e[0m\e[38;5;160m1\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m1\e[0m\e[38;5;160m}\e[0m\e[38;5;124m]\e[0m\e[38;5;124m]\e[0m\e[38;5;160m{\e[0m\e[38;5;9m(\e[0m\e[38;5;9m(\e[0m\e[38;5;9m1\e[0m\e[38;5;124m]\e[0m\e[38;5;88m<\e[0m\e[38;5;52m,\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m^\e[0m\e[38;5;124m?\e[0m\e[38;5;9m)\e[0m\e[38;5;160m1\e[0m\e[38;5;160m{\e[0m\e[38;5;160m{\e[0m\e[38;5;160m[\e[0m\e[38;5;160m]\e[0m\e[38;5;160m[\e[0m\e[38;5;9m1\e[0m\e[38;5;9m(\e[0m\e[38;5;160m{\e[0m\e[38;5;124m+\e[0m\e[38;5;52mI\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m.\e[0m\e[38;5;0m^\e[0m\e[38;5;0m \e[0m\e[38;5;0m\`\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;52ml\e[0m\e[38;5;160m1\e[0m\e[38;5;9m(\e[0m\e[38;5;160m}\e[0m\e[38;5;160m[\e[0m\e[38;5;160m[\e[0m\e[38;5;160m]\e[0m\e[38;5;160m]\e[0m\e[38;5;160m]\e[0m\e[38;5;124m-\e[0m\e[38;5;52mi\e[0m\e[38;5;52m,\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m\`\e[0m\e[38;5;0mI\e[0m\e[38;5;0m'\e[0m\e[38;5;0m^\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;88m<\e[0m\e[38;5;160m{\e[0m\e[38;5;124m_\e[0m\e[38;5;52mi\e[0m\e[38;5;88m<\e[0m\e[38;5;124m+\e[0m\e[38;5;88m<\e[0m\e[38;5;52m!\e[0m\e[38;5;52m:\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;0m^\e[0m\e[38;5;0m\"\e[0m\e[38;5;0m\"\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m'\e[0m\e[38;5;52m,\e[0m\e[38;5;0m'\e[0m\e[38;5;0m.\e[0m\e[38;5;0m\"\e[0m\e[38;5;52m,\e[0m\e[38;5;0m\`\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m \e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\n\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m\e[38;5;0m.\e[0m"

clear
echo -e $logo


echo -e "\n\n${RED} * GitHub ${CYAN}github.com/sidor0912/FunPayCardinal${RESET}"
echo -e "${RED} * Telegram ${CYAN}t.me/funpay_cardinal${RESET}"
echo -e "\n\n\n"


echo -ne "${CYAN}Введите имя пользователя, от имени которого будет запускаться бот (например, 'fpc' или 'cardinal'): ${RESET}"
while true; do
  read username
  if [[ "$username" =~ ^[a-zA-Z][a-zA-Z0-9_-]+$ ]]; then
    if id "$username" &>/dev/null; then
      echo -ne "\n${RED}Такой пользователь уже существует. ${CYAN}Пожалуйста, введите другое имя пользователя: ${RESET}"
    else
      break
    fi
  else
    echo -ne "\n${RED}Имя пользователя содержит недопустимые символы. ${CYAN}Имя должно начинаться с буквы и может включать только буквы, цифры, '_', или '-'. Пожалуйста, введите другое имя пользователя: ${RESET}"
  fi
done


distro_version=$(lsb_release -rs)


clear
echo -e "${start_process_line}\nДобавляю репозитории...\n${end_process_line}"


# 1
if ! sudo apt update ; then
  echo -e "${start_process_line}\nПроизошла ошибка при обновлении списка пакетов. (1/${commands})\n${end_process_line}"
  exit 2
fi

#2
if ! sudo apt install -y software-properties-common ; then
  echo -e "${start_process_line}\nПроизошла ошибка при установке software-properties-common. (2/${commands})\n${end_process_line}"
  exit 2
fi

#3
case $distro_version in
  "22.04" | "22.10" | "23.04" | "23.10" | "24.04" | "24.10") # Ubuntu 22.04 (Jammy Jellyfish), 22.10 (Kinetic Kudu), 23.04 (Lunar Lobster), 23.10 (Mantic Minotaur), 24.04 (Noble Numbat), 24.10 (Oracular Oriole)
    ;;
  "12") # Debian 12 (Bookworm)
    ;;
  "11") # Debian 11 (Bullseye)
    # TODO: Ошибка проверки ключа репозитория на некоторых машинах, хз почему, проще использовать костыль ввиде убунтовских deadsnakes
    # #3.1
    # if ! sudo curl -O https://people.debian.org/~paravoid/python-all/unofficial-python-all.asc ; then
    #   echo -e "${start_process_line}\nПроизошла ошибка при загрузке ключа репозитория. (3.1/${commands})\n${end_process_line}"
    #   exit 2
    # fi

    # #3.2
    # if ! sudo mv unofficial-python-all.asc /etc/apt/trusted.gpg.d/ ; then
    #   echo -e "${start_process_line}\nПроизошла ошибка при перемещении ключа репозитория. (3.2/${commands})\n${end_process_line}"
    #   exit 2
    # fi

    # #3.3
    # if ! echo "deb http://people.debian.org/~paravoid/python-all $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/python-all.list ; then
    #   echo -e "${start_process_line}\nПроизошла ошибка при добавлении репозитория. (3.3/${commands})\n${end_process_line}"
    #   exit 2
    # fi

    #3.1
    if ! sudo apt install -y gnupg ; then
      echo -e "${start_process_line}\nПроизошла ошибка при установке gnupg. (3.1/${commands})\n${end_process_line}"
      exit 2
    fi

    #3.2
    if ! sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys BA6932366A755776 ; then
      echo -e "${start_process_line}\nПроизошла ошибка при добавлении ключа репозитория. (3.2/${commands})\n${end_process_line}"
      exit 2
    fi

    #3.3
    if ! sudo add-apt-repository -s "deb https://ppa.launchpadcontent.net/deadsnakes/ppa/ubuntu focal main" ; then
      echo -e "${start_process_line}\nПроизошла ошибка при добавлении репозитория. (3.3/${commands})\n${end_process_line}"
      exit 2
    fi

    #3.4
    sudo tee /etc/apt/preferences.d/10deadsnakes-ppa >/dev/null <<EOF
Package: *
Pin: release o=LP-PPA-deadsnakes
Pin-Priority: 100
EOF
    if $? -ne 0 ; then
      echo -e "${start_process_line}\nПроизошла ошибка при добавлении приоритета репозитория. (3.4/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
  *)
    #3
    if ! sudo add-apt-repository -y ppa:deadsnakes/ppa ; then
      echo -e "${start_process_line}\nПроизошла ошибка при добавлении репозитория. (3/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
esac

#4
if ! sudo apt update ; then
  echo -e "${start_process_line}\nПроизошла ошибка при обновлении списка пакетов. (4/${commands})\n${end_process_line}"
  exit 2
fi


clear
echo -e "$start_process_line\nУстанавливаю необходимые пакеты...\n$end_process_line"


#5
if ! sudo apt install -y curl ; then
  echo -e "${start_process_line}\nПроизошла ошибка при установке Curl. (5/${commands})\n${end_process_line}"
  exit 2
fi

#6
if ! sudo apt install -y unzip ; then
  echo -e "${start_process_line}\nПроизошла ошибка при установке Unzip. (6/${commands})\n${end_process_line}"
  exit 2
fi


clear
echo -e "$start_process_line\nУстанавливаю Python...\n$end_process_line"


#7
case $distro_version in
  "24.04" | "24.10")
    if ! sudo apt install -y python3.12 python3.12-dev python3.12-gdbm python3.12-venv ; then
      echo -e "${start_process_line}\nПроизошла ошибка при установке Python. (7/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
  *)
    if ! sudo apt install -y python3.11 python3.11-dev python3.11-gdbm python3.11-venv ; then
      echo -e "${start_process_line}\nПроизошла ошибка при установке Python. (7/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
esac

clear
echo -e "$start_process_line\nСоздаю пользователя и устанавливаю/обновляю Pip...\n$end_process_line"

#8
if ! sudo useradd -m $username ; then
  echo -e "${start_process_line}\nПроизошла ошибка при создании пользователя. (8/${commands})\n${end_process_line}"
  exit 2
fi

#9
case $distro_version in
  "24.04" | "24.10")
    if ! sudo -u $username python3.12 -m venv /home/$username/pyvenv ; then
      echo -e "${start_process_line}\nПроизошла ошибка при создании виртуального окружения. (9/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
  *)
    if ! sudo -u $username python3.11 -m venv /home/$username/pyvenv ; then
      echo -e "${start_process_line}\nПроизошла ошибка при создании виртуального окружения. (9/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
esac

#10
# Важно: eunsurepip стоить запускать от root, иначе будет ошибка на некоторых версиях ОС (например, Debian 11, Debian 12, Ubuntu 20.04, Ubuntu 24.04)
if ! sudo /home/$username/pyvenv/bin/python -m ensurepip --upgrade ; then
  echo -e "${start_process_line}\nПроизошла ошибка при установке Pip. (10/${commands})\n${end_process_line}"
  exit 2
fi

#11
if ! sudo -u $username /home/$username/pyvenv/bin/python -m pip install --upgrade pip ; then
  echo -e "${start_process_line}\nПроизошла ошибка при обновлении Pip. (11/${commands})\n${end_process_line}"
  exit 2
fi

#12
if ! sudo chown -hR $username:$username /home/$username/pyvenv ; then
  echo -e "${start_process_line}\nПроизошла ошибка при изменении владельца виртуального окружения. (12/${commands})\n${end_process_line}"
  exit 2
fi


clear
echo -e "$start_process_line\nУстанавливаю FunPayCardinal...\n$end_process_line"


#13
if ! sudo mkdir /home/$username/fpc-install ; then
  echo -e "${start_process_line}\nПроизошла ошибка при создании директории для установки. (13/${commands})\n${end_process_line}"
  exit 2
fi

gh_repo="sidor0912/FunPayCardinal"
LOCATION=$(curl -sS https://api.github.com/repos/$gh_repo/releases/latest | grep "zipball_url" | awk '{ print $2 }' | sed 's/,$//' | sed 's/"//g' )

#14
if ! sudo curl -L $LOCATION -o /home/$username/fpc-install/fpc.zip ; then
  echo -e "${start_process_line}\nПроизошла ошибка при загрузке архива. (14/${commands})\n${end_process_line}"
  exit 2
fi

#15
if ! sudo unzip /home/$username/fpc-install/fpc.zip -d /home/$username/fpc-install ; then
  echo -e "${start_process_line}\nПроизошла ошибка при распаковке архива. (15/${commands})\n${end_process_line}"
  exit 2
fi

#16
if ! sudo mkdir /home/$username/FunPayCardinal ; then
  echo -e "${start_process_line}\nПроизошла ошибка при создании директории для бота. (16/${commands})\n${end_process_line}"
  exit 2
fi

#17
if ! sudo mv /home/$username/fpc-install/*/* /home/$username/FunPayCardinal/ ; then
  echo -e "${start_process_line}\nПроизошла ошибка при перемещении файлов. (17/${commands})\n${end_process_line}"
  exit 2
fi

#18
if ! sudo rm -rf /home/$username/fpc-install ; then
  echo -e "${start_process_line}\nПроизошла ошибка при удалении директории для установки. (18/${commands})\n${end_process_line}"
  exit 2
fi

#19
if ! sudo chown -hR $username:$username /home/$username/FunPayCardinal ; then
  echo -e "${start_process_line}\nПроизошла ошибка при изменении владельца файлов. (19/${commands})\n${end_process_line}"
  exit 2
fi

#20
if ! sudo -u $username /home/$username/pyvenv/bin/pip install -U -r /home/$username/FunPayCardinal/requirements.txt ; then
  echo -e "${start_process_line}\nПроизошла ошибка при установке необходимых Py-пакетов. (20/${commands})\n${end_process_line}"
  exit 2
fi


clear
echo -e "$start_process_line\nСоздаю ссылку на файл фонового процесса...\n$end_process_line"


#21
if ! sudo ln -sf /home/$username/FunPayCardinal/FunPayCardinal@.service /etc/systemd/system/FunPayCardinal@.service ; then
  echo -e "${start_process_line}\nПроизошла ошибка при создании ссылки на файл фонового процесса. (21/${commands})\n${end_process_line}"
  exit 2
fi


clear
echo -e "$start_process_line\nНастраиваю кодировку сервера...\n$end_process_line"


#22
case $distro_version in
  "11" | "12")
    if ! sudo apt install -y locales locales-all ; then
      echo -e "${start_process_line}\nПроизошла ошибка при установке локализаций. (22/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
  *)
    if ! sudo apt install -y language-pack-en ; then
      echo -e "${start_process_line}\nПроизошла ошибка при установке языковых пакетов. (22/${commands})\n${end_process_line}"
      exit 2
    fi
    ;;
esac


clear
echo -e $logo
echo -e '\n\n\e[1;91m * GitHub \e[1;96mgithub.com/sidor0912/FunPayCardinal\e[0m'
echo -e '\e[1;91m * Telegram \e[1;96mt.me/funpay_cardinal\e[0m'

echo -e "\n\n\e[1;92m################################################################################"
echo -e "Установка завершена."
echo -e "Запускаю первичную настройку..."
echo -e "################################################################################\e[0m"
sleep 3
clear


sudo -u $username LANG=en_US.utf8 /home/$username/pyvenv/bin/python /home/$username/FunPayCardinal/main.py <&1
sudo systemctl start FunPayCardinal@$username.service


clear
echo -e $logo
echo -e '\n\n\e[1;91m * GitHub \e[1;96mgithub.com/sidor0912/FunPayCardinal\e[0m'
echo -e '\e[1;91m * Telegram \e[1;96mt.me/funpay_cardinal\e[0m'

echo -e "\n\n\e[1;92m################################################################################"
echo -e "${RED}!СДЕЛАЙ СКРИНШОТ!${CYAN}!СДЕЛАЙ СКРИНШОТ!${RED}!СДЕЛАЙ СКРИНШОТ!${CYAN}!СДЕЛАЙ СКРИНШОТ!"
echo -e "\nГотово!"
echo -e "FPC запущен как фоновый процесс!"
echo -e "Теперь напиши своему Telegram-боту."
echo -e "\n\e[1;92mДля остановки FPC используй команду \e[93msudo systemctl stop FunPayCardinal@${username}\e[1;92m"
echo -e "Для запуска FPC используй команду \e[93msudo systemctl start FunPayCardinal@${username}\e[1;92m"
echo -e "Для перезапуска FPC используй команду \e[93msudo systemctl restart FunPayCardinal@${username}\e[1;92m"
echo -e "Для просмотра логов используй команду \e[93msudo systemctl status FunPayCardinal@${username} -n100\e[1;92m"
echo -e "Для добавления FPC в автозагрузку используй команду \e[93msudo systemctl enable FunPayCardinal@${username}\e[1;92m"
echo -e "${RED}* Перед добавлением FPC в автозагрузку убедись, что твой бот работает корректно.\e[1;92m"
echo -e "################################################################################\e[0m"

echo -ne "\n\n${CYAN}Сделал скриншот? ${PURPLE_LIGHT}Тогда нажми Enter, чтобы продолжить.${RESET}"
read
clear