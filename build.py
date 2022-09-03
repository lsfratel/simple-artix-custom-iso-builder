import os
import json
import subprocess
from pathlib import Path


PATH = Path(__file__).resolve().parent
PROFILES_PATH = Path(PATH, 'iso-profiles')
ISO_PATH = Path(PATH, 'iso')
SKELETON_PATH = Path(PATH, 'skeleton')
AUR_PACKAGES_PATH = Path(PATH, 'myrepo', 'packages')
ARTOOLS_CONFIG_PATH = Path(Path.home(), '.config', 'artools')
CONFIG = None


def run_cmd(cmd):
    resp = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL)
    return True if resp.returncode == 0 else False


def log(msg: str):
    print('==>', msg.upper())


def check_system():
    assert run_cmd('command -v buildiso'), 'Please install buildiso, aborting.'
    assert run_cmd(
        'lsmod | grep loop'), 'Please modprobe the loop module, aborting.'

    check_paths()

    if not Path(PROFILES_PATH, 'base').exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/base {PROFILES_PATH.absolute()}'), 'Can\'t copy base profile, aborting.'

    if not Path(PROFILES_PATH, 'common').exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/common {PROFILES_PATH.absolute()}'), 'Can\'t copy common profile, aborting.'

    if not Path(PROFILES_PATH, CONFIG['name']).exists():
        assert run_cmd(
            f'cp -a /usr/share/artools/iso-profiles/{CONFIG["base"]} {PROFILES_PATH.joinpath(CONFIG["name"]).absolute()}'), 'Can\'t copy main profile, aborting.'

    assert run_cmd(
        f'cp /usr/share/artools/makepkg.conf {ARTOOLS_CONFIG_PATH.absolute()}'), 'Can\'t copy makepkg.conf, aborting.'
    assert run_cmd(
        f'cp /usr/share/artools/pacman-default.conf {ARTOOLS_CONFIG_PATH.absolute()}'), 'Can\'t copy pacman-default.conf, aborting.'
    assert run_cmd(
        f'cp -a /etc/artools/./ {ARTOOLS_CONFIG_PATH.absolute()}'), 'Can\'t copy artools-{base,pkg,iso}.conf, aborting.'

    try:
        with open(ARTOOLS_CONFIG_PATH.joinpath('pacman-default.conf'), 'a') as f:
            f.writelines(
                ['\n[extra]\n', 'Include = /etc/pacman.d/mirrorlist-arch\n'])
            f.writelines(
                ['\n[community]\n', 'Include = /etc/pacman.d/mirrorlist-arch'])
            f.writelines(['\n[myrepo]\n', 'SigLevel = Optional TrustAll\n',
                          f'Server = file:///{AUR_PACKAGES_PATH.parent.absolute()}'])
    except:
        log('Can\'t add archlinux mirros to pacman.conf, aborting.')

    try:
        with open(ARTOOLS_CONFIG_PATH.joinpath('artools-base.conf'), 'a') as f:
            f.write(f'\nWORKSPACE_DIR="{PATH}"')
    except:
        log('Can\'t set WORKSPACE_DIR in artools-base.conf, aborting.')

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
                path = PROFILES_PATH.joinpath(p, kk).absolute()
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

    log('Successfully processed packages.')


def copy_skeleton():
    assert run_cmd(
        f'rsync -av {SKELETON_PATH.absolute()}/ {PROFILES_PATH.joinpath(CONFIG["name"], "root-overlay")}'), 'Can\'t copy skeleton, aborting.'
    log('Successfully copied skeleton.')


def build_aur_packages():
    gitlink = 'https://aur.archlinux.org/'

    for pkg in CONFIG['aur']:
        path = AUR_PACKAGES_PATH.joinpath(pkg)
        if path.exists():
            continue
        assert run_cmd(
            f'git clone {gitlink}{pkg}.git {AUR_PACKAGES_PATH.joinpath(pkg).absolute()}'), f'Can\'t download pkg: {pkg}, aborting.'

        os.chdir(path.absolute())
        assert run_cmd(
            'makepkg -sr --noconfirm'), f'Can\'t makepkg {pkg}, aborting.'
        assert run_cmd(
            'mv *.zst ../../'), f'Can\'t move {pkg} to repo directory, aborting.'

    os.chdir(PATH.joinpath('myrepo'))
    assert run_cmd(
        'repo-add -n myrepo.db.tar.gz *.zst'), 'Can\'t add build pkgs to repo databse, aborting.'
    os.chdir(PATH.absolute())
    log('Successfully updated aur packages.')


def set_services():
    with open(PROFILES_PATH.joinpath(CONFIG['name'], 'profile.conf').absolute(), 'r+') as f:
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

    cmds = [
        f'buildiso -p {CONFIG["name"]} -t {PATH.joinpath("iso").absolute()} -i {CONFIG["init"]} -x',
        f'artix-chroot /var/lib/artools/buildiso/{CONFIG["name"]}/artix/rootfs < ./configure.sh',
        f'buildiso -p {CONFIG["name"]} -t {PATH.joinpath("iso").absolute()} -i {CONFIG["init"]} -sc',
        f'buildiso -p {CONFIG["name"]} -t {PATH.joinpath("iso").absolute()} -i {CONFIG["init"]} -bc',
        f'buildiso -p {CONFIG["name"]} -t {PATH.joinpath("iso").absolute()} -i {CONFIG["init"]} -zc'
    ]

    for c in cmds:
        subprocess.run(c, shell=True)


def check_paths():
    if not PROFILES_PATH.exists():
        PROFILES_PATH.mkdir()

    if not ISO_PATH.exists():
        ISO_PATH.mkdir()

    if not SKELETON_PATH.exists():
        SKELETON_PATH.mkdir()

    if not AUR_PACKAGES_PATH.exists():
        AUR_PACKAGES_PATH.mkdir(parents=True)

    if not ARTOOLS_CONFIG_PATH.exists():
        ARTOOLS_CONFIG_PATH.mkdir(parents=True)


if __name__ == '__main__':

    with open('config.json', 'r') as f:
        CONFIG = json.load(f)

    start()
