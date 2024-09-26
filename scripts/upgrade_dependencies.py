# This program is used to chek if:
#  * there is any addon installed from a github pull request that has been merged and could be updated
#  * there is any addon that could be updated to the latest version available on pypi.
# It collect addons installed from a github pull request that has been merged and addons installed from pypi.
# For each addon collected:
#  - It check if a newer version is available on pypi
#  - It launch the 'pip-wheel-diff' command to compare the installed wheel with the wheel of the latest version available on pypi
#  - It ask if you want to update the addon
#  - If you say yes, it remove the reference to the installed version in the requirements files and launch pip-df sync to update the addon
#  - Once it's done it commit the change.
# pip-wheel-diff and pip-df tools must be installed to use this script.
# a way to use it:
#    uvx run scripts/upgrade_dependencies.py --odoo-version 16.0
#  or
#    pipx run scripts/upgrade_dependencies.py --odoo-version 16.0
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "pip-wheel-diff",
#   "pip-deepfreeze",
# ]
# ///

import os
import re
import subprocess
import sys
from collections import namedtuple

import click
import httpx
from packaging import version as packaging_version

PR = namedtuple("PR", ["addon", "org", "repo", "pr"])

PR_INFO = namedtuple("PR_INFO", ["pr", "file", "requirement_line"])


PR_URL_RE = re.compile(
    r".*odoo-addon-(?P<addon>[^@]+).*github.com.(?P<org>[^/]+)/(?P<repo>[^/.]+).*@refs/pull/(?P<pr>[0-9]+)/head"
)

# addon as odoo-addon-<addon> == <version>
ADDON_RE = re.compile(r"odoo-addon-(?P<addon>[^=]+)==(?P<version>.*)")

ADDON_INFO = namedtuple("ADDON_INFO", ["addon", "version", "file", "requirement_line"])

HTTPX_CLIENT = None


def looks_like_req_file(filename):
    return ("requirements" in filename or "constraints" in filename) and (
        filename.endswith(".txt") or filename.endswith(".txt.in")
    )


def display_state(state, merged):
    if state == "open":
        return click.style("open", fg="white")
    elif state == "closed" and merged:
        return click.style("merged", fg="magenta")
    elif state == "closed" and not merged:
        return click.style("closed", fg="red")
    else:
        return click.style(state, fg="yellow")


def is_pr_merged(pr):
    r = HTTPX_CLIENT.get(
        f"https://api.github.com/repos/{pr.org}/{pr.repo}/pulls/{pr.pr}"
    )
    try:
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        click.echo(click.style(f"Failed to fetch PR {pr} status: {e}", fg="red"))
        return False
    rjson = r.json()
    state = rjson["state"]
    merged = rjson["merged"]
    if state == "closed" and merged:
        return True
    state = display_state(state, merged)
    click.echo(f"https://github.com/{pr.org}/{pr.repo}/pull/{pr.pr} is {state}")
    return False


def search_addons(only_merged=False, only_released=False):
    addons_info = []
    for reqfile in os.listdir("."):
        if not looks_like_req_file(reqfile):
            continue
        click.echo("Scanning " + reqfile)
        with open(reqfile) as f:
            for line in f:
                if not only_released:
                    mo = PR_URL_RE.match(line)
                    if mo:
                        pr = PR(**mo.groupdict())
                        if is_pr_merged(pr):
                            addons_info.append(
                                ADDON_INFO(
                                    addon=pr.addon,
                                    version=None,
                                    requirement_line=line,
                                    file=reqfile,
                                )
                            )
                        continue
                if not only_merged:
                    mo = ADDON_RE.match(line)
                    if not mo:
                        continue
                    addons_info.append(
                        ADDON_INFO(
                            **mo.groupdict(), requirement_line=line, file=reqfile
                        )
                    )
    return addons_info


def get_latest_version(addon, odoo_version):
    response = httpx.Client().get(f"https://pypi.org/pypi/odoo-addon-{addon}/json")
    if response.status_code != 200:
        click.echo(click.style(f"Failed to get latest version of {addon}", fg="red"))
        return
    releases = response.json()["releases"]
    if not releases:
        click.echo(click.style(f"No releases found for {addon}", fg="red"))
        return
    # get the latest version that is compatible with the odoo version
    latest_version = None
    for released_version in releases.keys():
        if released_version.startswith(odoo_version):
            if not latest_version:
                latest_version = released_version
                continue
            if packaging_version.parse(released_version) > packaging_version.parse(
                latest_version
            ):
                latest_version = released_version
    if not latest_version:
        click.echo(
            click.style(
                f"No version of {addon} is compatible with odoo {odoo_version}",
                fg="red",
            )
        )
        return
    click.echo(f"Latest version of {addon} is {latest_version}")
    return latest_version


def diff_wheel(requirement_line, addon, version):
    args = [
        "pip-wheel-diff",
        requirement_line.strip(),
        f"odoo-addon-{addon}=={version}",
    ]
    click.echo("Running: " + " ".join(args))
    subprocess.run(args, capture_output=True)


def remove_line_from_file(line, file):
    line_pattern = re.sub(r"([/@#])", r"\\\1", line)
    args = ["sed", "-i", f"/{line_pattern}/d", file]
    click.echo("Running: " + " ".join(args))
    ret = subprocess.run(args, capture_output=True)
    if ret.returncode != 0:
        click.echo(click.style(f"Failed to remove line from {file}", fg="red"))
        return False
    return True


def upgrade_addon(addon):
    args = ["pip-df", "sync", "--installer", "uvpip", "--update", "odoo-addon-" + addon]
    click.echo("Running: " + " ".join(args))
    ret = subprocess.run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
    if ret.returncode != 0:
        click.echo(click.style(f"Failed to update {addon}", fg="red"))
        return False
    return True


def commit_change(addon, version):
    addon = addon.replace("-", "_")
    args = ["git", "commit", "-am", f"[UPG] {addon}: Upgrade up to {version}"]
    click.echo("Running: " + " ".join(args))
    ret = subprocess.run(args, capture_output=True)
    if ret.returncode != 0:
        click.echo(click.style("Failed to commit the change", fg="red"))
        return False
    return True


def do_upgrade_process(
    addon, requirement_line, file, current_version=None, odoo_version=None
):
    #  compare version with latest version on pypi
    latest_version = get_latest_version(addon, odoo_version)
    if not latest_version:
        return False

    if current_version and packaging_version.parse(
        current_version
    ) >= packaging_version.parse(latest_version):
        click.echo(f"{addon} is already up to date (version {current_version})")
        return False

    diff_wheel(requirement_line, addon, latest_version)
    # ask if we want to update the requirement
    update = (
        input(f"Do you want to update {addon} to version {latest_version}? (y/n): ")
        .strip()
        .lower()
    )
    if update == "y":
        ret = remove_line_from_file(requirement_line, file)
        if not ret:
            return False
        ret = upgrade_addon(addon)
        if not ret:
            raise Exception(
                f"Failed to upgrade addon but the line has been removed from {file}"
            )
        ret = commit_change(addon, latest_version)
        if not ret:
            raise Exception(
                f"Failed to commit the change but the line has been removed from {file}"
            )
        return True
    return False


@click.command()
@click.option("--only-merged", is_flag=True, help="Only process merged PRs")
@click.option("--only-released", is_flag=True, help="Only process released addons")
@click.option("--odoo-version", help="Odoo version to use", required=True)
def main(only_merged, only_released, odoo_version):
    global HTTPX_CLIENT
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        HTTPX_CLIENT = httpx.Client(headers={"Authorization": f"token {token}"})
    else:
        click.echo("No GITHUB_TOKEN found in env, using anonymous access")
        HTTPX_CLIENT = httpx.Client()
    addons_info = search_addons(only_merged, only_released)
    if not addons_info:
        click.echo("No addons found")
        return
    upgraded_addons = set()
    for info in addons_info:
        addon = info.addon.strip()
        file = info.file.strip()
        requirement_line = info.requirement_line.strip()
        current_version = info.version.strip()
        click.echo(f"Try to upgrade addon {info.addon} found in {file}")
        ret = do_upgrade_process(
            addon, requirement_line, file, current_version, odoo_version
        )
        if ret:
            upgraded_addons.add(addon)
    if upgraded_addons:
        click.echo(
            f"Successfully upgraded {len(upgraded_addons)} addons: {', '.join(upgraded_addons)}"
        )


if __name__ == "__main__":
    main()
