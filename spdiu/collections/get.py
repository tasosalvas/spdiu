#!/usr/bin/env python
# Copyright (C) 2025 Tasos Alvas <tasos.alvas@qwertyuiopia.com>
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
SPDIU Download and installation tasks.
"""

import os
import shutil
import stat

import urllib.request
from zipfile import ZipFile, BadZipFile

from invoke import task, Collection

from .. import util


ns = Collection('get')


@task
def latest(c):
    """
    Returns the latest version by checking github's 'releases/latest'.
    """
    cfg = c.config.spdiu

    l_url = '/'.join((cfg.release_github, 'latest'))
    with urllib.request.urlopen(l_url) as r:
        r_url = r.geturl()
        version = r_url.split('/')[-1]

    print(f"The latest version is {version}")
    return version


@task
def install(c, version=None):
    """
    Downloads the latest game release from github. 'inv -h' this for more options.

    -v, --version [release] to request a version.

    See invoke.yaml.example for configuring the task to download different SPD forks.
    """
    cfg = c.config.spdiu

    tpl = cfg.release_template
    platform = cfg.release_platform
    ext = cfg.release_extension

    packages = os.path.join(os.path.expanduser(cfg.base_dir), cfg.release_packages)
    install_path = os.path.expanduser(cfg.game_dir)


    # Determine the version
    if cfg.release_version:
        r_url = '/'.join((cfg.release_github, cfg.release_version))

    elif version:
        r_url = '/'.join((cfg.release_github, version))

    else:
        version = latest(c)


    # Don't put arbitrary code in your user config, mkay?
    f_url = '/'.join((cfg.release_github, eval('f"' + tpl + '"')))
    f_name = f_url.split('/')[-1]

    p_path = os.path.join(packages, f_name)
    os.makedirs(packages, exist_ok=True)


    # Get ready to download
    def progress_hook(blocks, block_size, total):
        current_mb = blocks * block_size / 1024**2
        total_mb = total / 1024**2
        percentage = current_mb / total_mb

        chars = 30
        full = int(chars * percentage) * "="
        bar = full.ljust(chars, '-')

        print(f" |>{bar}<| {current_mb:.2f}MB out of {total_mb:.2f}MB", end='\r')


    # Downloading
    if os.path.exists(p_path):
        print(f"{f_name} already exists in {cfg.release_packages}.")

    elif ext == 'jar' and os.path.exists(os.path.join(install_path, f_name)):
        print('This jar file is already installed, nothing to do.')
        return

    else:
        print(f"Downloading {f_name}...")

        try:
            urllib.request.urlretrieve(f_url, p_path, progress_hook)

        except urllib.error.HTTPError:
            print(f'404: {f_url} not found.')
            return

        except urllib.error.ContentTooShortError:
            os.remove(p_path)
            print('Transfer failed, try again.')
            return

        print('Package downloaded. Great success!')


    # Pre-installation checks
    if os.path.exists(install_path):
        print('WARNING: Destination already exists.')
        print(install_path)

        delete_ok = input('Are you sure you want to delete it? (y/N)')
        if delete_ok.strip().lower() == 'y':
            util.remove(install_path)

        else:
            print('Well, come back when you\'re ready.')
            return


    # Installation, varying by package
    print(f"Installing {f_name}...")
    os.makedirs(install_path, exist_ok=True)


    if ext == 'zip':
        with ZipFile(p_path, 'r') as z:
            try:
                z.extractall(install_path)
                print('Zip package extracted to the game folder.')

            except BadZipFile:
                os.remove(p_path)
                print('Zip file is unreadable. Removed it, try again.')


        # Python's zipfile doesn't preserve permissions when extracting
        if platform.lower() == 'linux':
            binary = os.path.join(install_path, cfg.game_cmd)
            permissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
            os.chmod(binary, permissions)


    elif ext == 'jar':
        shutil.move(p_path, install_path)
        print('Jar package copied to the game folder.')


    print(f"{f_name} was successfully installed. Have a nice day!")


ns.add_task(latest)
ns.add_task(install)
