#!/usr/bin/env bash

set -e -x

sed -i "s/#en_US.UTF-8/en_US.UTF-8/" /etc/locale.gen
sed -i "s/#pt_BR.UTF-8/pt_BR.UTF-8/" /etc/locale.gen

cat >"/etc/locale.conf" <<EOF
LANG="en_US.UTF-8"
LC_COLLATE="C"
EOF

locale-gen

rm -R /root/.gnupg/
gpg --refresh-keys

pacman-key --init
pacman-key --populate artix
pacman-key --refresh-keys

tee -a "/etc/pacman.conf" <<"EOF"

[universe]
Server = https://mirror1.artixlinux.org/universe/$arch
Server = https://mirror.pascalpuffke.de/artix-universe/$arch
Server = https://artixlinux.qontinuum.space/artixlinux/universe/os/$arch
Server = https://mirror1.cl.netactuate.com/artix/universe/$arch
Server = https://ftp.crifo.org/artix-universe/
Server = https://universe.artixlinux.org/$arch
EOF

pacman -Sy
pacman -S --noconfirm --needed artix-keyring archlinux-keyring artix-archlinux-support
pacman-key --populate archlinux

tee -a "/etc/pacman.conf" <<"EOF"

# ARCHLINUX
[extra]
Include = /etc/pacman.d/mirrorlist-arch

[community]
Include = /etc/pacman.d/mirrorlist-arch

#[multilib]
#Include = /etc/pacman.d/mirrorlist-arch
EOF

sed -i '/^load-module module-filter-apply/a .ifexists module-echo-cancel.so\nload-module module-echo-cancel aec_method=webrtc aec_args="analog_gain_control=0 digital_gain_control=0"\n.endif' /etc/pulse/default.pa

pacman -Scc --noconfirm

rm archlinux-key*

adir="/usr/share/applications"
apps=(avahi-discover.desktop bssh.desktop bvnc.desktop echomixer.desktop \
	envy24control.desktop exo-preferred-applications.desktop feh.desktop \
	hdajackretask.desktop hdspconf.desktop hdspmixer.desktop \
    hwmixvolume.desktop lftp.desktop libfm-pref-apps.desktop \
    lxshortcut.desktop lstopo.desktop networkmanager_dmenu.desktop \
    pcmanfm-desktop-pref.desktop qv4l2.desktop qvidcap.desktop \
    stoken-gui.desktop stoken-gui-small.desktop thunar-bulk-rename.desktop \
	thunar-settings.desktop thunar-volman-settings.desktop yad-icon-browser.desktop \
    rofi.desktop rofi-theme-selector.desktop picom.desktop parcellite.desktop \
    mictray.desktop volumeicon.desktop nm-applet.desktop lxsession-edit.desktop \
    lxsession-default-apps.desktop)

for app in "${apps[@]}";
do
	if [[ -e "$adir/$app" ]];
    then
        sed -i '$s/$/\nNoDisplay=true/' "$adir/$app"
	fi
done
