#!/usr/bin/env bash

## Window rules ----------------------------------------------#

# remove all rules first
bspc rule -r *:*

## 1 > terminal (always open terminal on workspace-1)
bspc rule -a Alacritty desktop='^1' follow=on focus=on
bspc rule -a Xfce4-terminal desktop='^1' follow=on focus=on

## 2 > web (always open web browser on workspace-2)
bspc rule -a firefox desktop='^2' follow=on focus=on
bspc rule -a chromium desktop='^2' follow=on focus=on

## 3 > files (always open file manager on workspace-3)
declare -a files=(Pcmanfm Thunar qBittorrent)
for i in ${files[@]}; do
   bspc rule -a $i desktop='^3' follow=on focus=on; done

## 4 > code (always open editors on workspace-4)
declare -a code=(Geany code-oss)
for i in ${code[@]}; do
   bspc rule -a $i desktop='^4' follow=on focus=on; done

## 5 > office and docs (always open office/doc apps on workspace-5)
declare -a office=(Gucharmap Atril Evince \
libreoffice-writer libreoffice-calc libreoffice-impress \
libreoffice-startcenter libreoffice Soffice *:libreofficedev *:soffice)
for i in ${office[@]}; do
   bspc rule -a $i desktop='^5' follow=on focus=on; done

## 6 > communication (always open communication apps on workspace-6)
declare -a comm=(Thunderbird TelegramDesktop Hexchat)
for i in ${comm[@]}; do
   bspc rule -a $i desktop='^6' follow=on focus=on; done

## 7 > media (always open media apps on workspace-7)
declare -a media=(Audacity Music MPlayer Lxmusic Inkscape Gimp-2.10 obs)
for i in ${media[@]}; do
   bspc rule -a $i desktop='^7' state=floating follow=on focus=on; done

## 8 > system (always open system apps on workspace-8)
bspc rule -a 'VirtualBox Manager' desktop='^8' follow=on focus=on
bspc rule -a GParted desktop='^8' follow=on focus=on
declare -a settings=(Lxappearance Lxtask Lxrandr Arandr \
System-config-printer.py Pavucontrol Exo-helper-1 \
Xfce4-power-manager-settings)
for i in ${settings[@]}; do
   bspc rule -a $i desktop='^8' state=floating follow=on focus=on; done

## Always Floating Apps
declare -a floating=(alacritty-float Pcmanfm Thunar Onboard Yad 'Firefox:Places' \
Viewnior feh Nm-connection-editor)
for i in ${floating[@]}; do
   bspc rule -a $i state=floating follow=on focus=on; done

bspc rule -a Conky state=floating manage=off
bspc rule -a stalonetray state=floating manage=off