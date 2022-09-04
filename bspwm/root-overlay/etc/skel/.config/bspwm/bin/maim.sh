#!/usr/bin/env bash

func_select_copy() {
    maim -s | xclip -selection clipboard -t image/png
    notify-send "Screenshot" "Copiado para a área de transferência!" -i flameshot
}

func_select_save() {
    maim -s "$(xdg-user-dir PICTURES)/$(date +%Y-%m-%d_%H-%M-%S).png"
    notify-send "Screenshot" "Salvo na pasta de imagens" -i flameshot
}

while getopts ":cs" option; do
    case $option in
        c)
            func_select_copy
            exit ;;
        s)
            func_select_save
            exit;;
        \?)
            echo "Invalid option"
            exit ;;
    esac
done
