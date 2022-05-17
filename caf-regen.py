#!/usr/bin/env python3

from bs4 import BeautifulSoup
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET


def groups_for_repo(repo, extra=[]):
    groups = set(extra)

    if re.match(r"device/.*[_-]kernel", repo):
        groups.add("kernel")

    if re.match(r"kernel/prebuilts/", repo):
        groups.add("kernel")

    if re.match(r"device/generic/.*mips", repo):
        groups.add("mips")

    if re.match(r"platform/prebuilts/.*/mips/.*", repo):
        groups.add("mips")

    if repo == "platform/external/chromium-webview":
        groups.add("chromium")

    if repo.startswith("platform/hardware/bsp/"):
        groups.add("bsp")

    if re.match(r"platform/prebuilts/.*darwin(-x86)?.*", repo):
        groups.add("darwin")

    if re.match(r"platform/prebuilts/.*windows(-x86)?.*", repo):
        groups.add("windows")

    return sorted(groups)


def get_all_repos():
    repos = set()

    try:
        caf = urllib.request.urlopen(
            urllib.request.Request("https://source.codeaurora.org/quic/la/")
        ).read()
    except urllib.error.HTTPError as e:
        sys.exit(e)
    soup = BeautifulSoup(caf, "html.parser")

    for repo in soup.find_all(class_="sublevel-repo"):
        repos.add(repo.a["href"][9:-1])  # Drop /quic/la/

    return repos


# Generate groups for all repositories
repos = {}
for repo in get_all_repos():
    repos[repo] = groups_for_repo(repo)

file = open("caf.xml", "w")
file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
file.write("<manifest>\n")
file.write("\n")
file.write('  <remote  name="caf"\n')
file.write('           review="https://source.codeaurora.org/quic/la/"\n')
file.write('           fetch="https://source.codeaurora.org/quic/la/" />\n')
file.write('  <default revision="master"\n')
file.write('           remote="caf"\n')
file.write('           sync-j="4" />\n')
file.write("\n")

for repo in sorted(repos):
    line = 'name="' + repo + '"'

    # Would we get a path conflict?
    if any(s.startswith(repo + "/") for s in repos):
        line += ' path="' + repo + '_git"'
    else:
        line += ' path="' + repo + '"'

    # Add groups
    groups = repos[repo]
    if len(groups) > 0:
        line += ' groups="' + ",".join(groups) + '"'

    file.write("  <project " + line + " />\n")

file.write("</manifest>\n")
file.close()
