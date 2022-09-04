"""
Artix custom iso builder.

Usage:
    builder.py --config <config_path>
    builder.py (-h | --help)

Options:
    --config    The config file to load
    -h, --help   Show this help text

"""

import os
import json
import subprocess
from pathlib import Path
from docopt import docopt


CONFIG = dict()

PATH = Path(__file__).resolve().parent
PROFILES_PATH = Path(PATH, 'iso-profiles')
ISO_PATH = Path(PATH, 'iso')
SKELETON_PATH = Path(PATH, 'skeleton')
AUR_PACKAGES_PATH = Path('/tmp')
MYREPO_PATH = Path(PATH, 'myrepo')
ARTOOLS_CONFIG_PATH = Path(Path.home(), '.config', 'artools')


def update_config(conf):
    global CONFIG, SKELETON_PATH
    CONFIG = conf
    SKELETON_PATH = Path(CONFIG['skeleton'])


def run_cmd(cmd):
    resp = subprocess.run(cmd, shell=True)
    return True if resp.returncode == 0 else False


def log(msg: str):
    print('==>', msg.upper())


def check_system():
    assert run_cmd('command -v buildiso'), 'Please install buildiso, aborting.'
    assert run_cmd(
        'lsmod | grep loop'), 'Please modprobe the loop module, aborting.'

    if not PROFILES_PATH.exists():
        PROFILES_PATH.mkdir()

    if not ISO_PATH.exists():
        ISO_PATH.mkdir()

    if not SKELETON_PATH.exists():
        SKELETON_PATH.mkdir()

    if not MYREPO_PATH.exists():
        MYREPO_PATH.mkdir(parents=True)

    if not ARTOOLS_CONFIG_PATH.exists():
        ARTOOLS_CONFIG_PATH.mkdir(parents=True)

    if not Path(PROFILES_PATH, 'base').exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/base {PROFILES_PATH}'), 'Can\'t copy base profile, aborting.'

    if not Path(PROFILES_PATH, 'common').exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/common {PROFILES_PATH}'), 'Can\'t copy common profile, aborting.'

    if not Path(PROFILES_PATH, CONFIG['name']).exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/{CONFIG["base"]} {PROFILES_PATH.joinpath(CONFIG["name"])}'), 'Can\'t copy main profile, aborting.'

    assert run_cmd(
        f'cp /usr/share/artools/makepkg.conf {ARTOOLS_CONFIG_PATH}'), 'Can\'t copy makepkg.conf, aborting.'
    assert run_cmd(
        f'cp /usr/share/artools/pacman-default.conf {ARTOOLS_CONFIG_PATH}'), 'Can\'t copy pacman-default.conf, aborting.'
    assert run_cmd(
        f'cp -a /etc/artools/./ {ARTOOLS_CONFIG_PATH}'), 'Can\'t copy artools-{base,pkg,iso}.conf, aborting.'

    try:
        with open(ARTOOLS_CONFIG_PATH.joinpath('pacman-default.conf'), 'a') as f:
            f.writelines(
                ['\n[extra]\n', 'Include = /etc/pacman.d/mirrorlist-arch\n'])
            f.writelines(
                ['\n[community]\n', 'Include = /etc/pacman.d/mirrorlist-arch'])
            f.writelines(['\n[myrepo]\n', 'SigLevel = Optional TrustAll\n',
                          f'Server = file:///{MYREPO_PATH}'])
    except:
        log('Can\'t add archlinux mirros to pacman.conf, aborting.')
        exit(1)

    try:
        with open(ARTOOLS_CONFIG_PATH.joinpath('artools-base.conf'), 'a') as f:
            f.write(f'\nWORKSPACE_DIR="{PATH}"')
    except:
        log('Can\'t set WORKSPACE_DIR in artools-base.conf, aborting.')
        exit(1)

    log('System check OK!')


def process_packages():
    try:
        packages = CONFIG['packages']
        for k in packages.keys():
            added = []
            for kk in packages[k].keys():
                if k == '$name':
                    p = CONFIG['name']
                else:
                    p = k
                path = PROFILES_PATH.joinpath(p, kk)
                with open(path, 'r+') as f:
                    lines = f.readlines()
                    f.seek(0)
                    if packages[k][kk]['remove'] == '*':
                        f.truncate()
                        for pkg in packages[k][kk]['add']:
                            if pkg not in added:
                                added.append(pkg)
                                f.write(f'\n{pkg}')
                        continue
                    for pkg in lines:
                        if pkg.strip() not in packages[k][kk]['remove']:
                            if pkg not in added:
                                added.append(pkg.strip())
                                f.write(pkg)
                    for pkg in packages[k][kk]['add']:
                        if pkg not in added:
                            added.append(pkg)
                            f.write(f'\n{pkg}')
                    f.truncate()
    except:
        log('Can\'t process packages in config.json, aborting.')
        exit(1)

    log('Successfully processed packages.')


def copy_skeleton():
    assert run_cmd(
        f'rsync -av {SKELETON_PATH}/root-overlay/ {PROFILES_PATH.joinpath(CONFIG["name"], "root-overlay")}'), 'Can\'t copy skeleton root-overlay, aborting.'
    assert run_cmd(
        f'rsync -av {SKELETON_PATH}/live-overlay/ {PROFILES_PATH.joinpath(CONFIG["name"], "live-overlay")}'), 'Can\'t copy skeleton live-overlay, aborting.'
    log('Successfully copied skeleton.')


def build_aur_packages():
    gitlink = 'https://aur.archlinux.org/'
    myrepo_pkgs = str(subprocess.check_output(f'ls {MYREPO_PATH}', shell=True))

    for pkg in CONFIG['aur']:
        if not CONFIG['re-build-aur']:
            if pkg in myrepo_pkgs:
                log(f'Skipping {pkg}, already build.')
                continue
        path = AUR_PACKAGES_PATH.joinpath(pkg)
        if path.exists():
            run_cmd(f'rm -rf {path}'), f'Can\'t remove dir: {path}'
        assert run_cmd(
            f'git clone {gitlink}{pkg}.git {AUR_PACKAGES_PATH.joinpath(pkg)}'), f'Can\'t download pkg: {pkg}, aborting.'

        os.chdir(path)
        assert run_cmd(
            'makepkg -sr --noconfirm'), f'Can\'t makepkg {pkg}, aborting.'
        assert run_cmd(
            f'mv *.zst {MYREPO_PATH}'), f'Can\'t move {pkg} to repo directory, aborting.'

    os.chdir(MYREPO_PATH)
    assert run_cmd(
        'repo-add -n myrepo.db.tar.gz *.zst'), 'Can\'t add build pkgs to repo databse, aborting.'
    os.chdir(PATH)
    log('Successfully updated aur packages.')


def set_services():
    with open(PROFILES_PATH.joinpath(CONFIG['name'], 'profile.conf'), 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        for line in lines:
            if not line.startswith('SERVICES='):
                f.write(line)
            else:
                services = " ".join(f"'{w}'" for w in CONFIG["services"])
                f.write(f'SERVICES=({services})\n')
        f.truncate()
    log('Successfully updated services.')


def start():
    check_system()
    process_packages()
    set_services()
    copy_skeleton()
    build_aur_packages()

    args = f'-p {CONFIG["name"]} -t {ISO_PATH} -i {CONFIG["init"]}'

    cmds = [
        f'buildiso {args} -x',
        f'artix-chroot /var/lib/artools/buildiso/{CONFIG["name"]}/artix/rootfs < {SKELETON_PATH.joinpath("configure.sh")}',
        f'buildiso {args} -sc',
        f'buildiso {args} -bc',
        f'buildiso {args} -zc'
    ]

    for c in cmds:
        subprocess.run(c, shell=True)


if __name__ == '__main__':
    args = docopt(__doc__)

    with open(args['<config_path>'], 'r') as f:
        update_config(json.load(f))

    start()
