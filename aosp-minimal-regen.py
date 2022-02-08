#!/usr/bin/env python3

import os
import re
import sys
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


def get_git_repo(url, path):
    if os.path.isdir(path):
        print("Updating {} repository...".format(path))
        repo = git.Repo(path)
        repo.remote("origin").fetch()
    else:
        print("Downloading {} repository...".format(path))
        repo = git.Repo.clone_from(url, path)

    return repo


def parse_all_refs(manifest, refs):
    repos = set()

    for index, ref in enumerate(refs, 1):
        print("[{}/{}] Parsing `{}`...".format(index, len(refs), ref))

        # Load the XML
        manifest_xml = ET.fromstring(manifest.git.show("{}:default.xml".format(ref)))

        for child in manifest_xml:
            # Skip all non-project tags
            if child.tag != "project":
                continue

            repos.add(child.attrib["name"])

    return repos


try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repositories
platform_manifest = get_git_repo("https://android.googlesource.com/platform/manifest", "aosp_manifest")
kernel_manifest = get_git_repo("https://android.googlesource.com/kernel/manifest", "aosp_kernel_manifest")

# Get all the refs
platform_refs = [tag for tag in sorted(platform_manifest.git.tag(l=True).splitlines())]  # All the tags...
platform_refs.append('origin/master')  # ...and master
kernel_refs = [ref.name for ref in kernel_manifest.refs]  # All the refs, repo only has branches no tags...

# Skip a broken kernel ref
kernel_refs.remove("origin/android-gs-raviole-mainline")

# Look for repo names in each ref
platform_repos = parse_all_refs(platform_manifest, platform_refs)
kernel_repos = parse_all_refs(kernel_manifest, kernel_refs)

# Always add the manifest so one can sync from this mirror
platform_repos.add("platform/manifest")
kernel_repos.add("kernel/manifest")

# Include repositories that we added to the default manifest ourselves
platform_repos.add("platform/prebuilts/gas/linux-x86")

# Remove kernel repositories that are already in the platform manifest
kernel_repos = kernel_repos - platform_repos

# Generate groups for all repositories
repos = {}
for repo in platform_repos:
    repos[repo] = groups_for_repo(repo)
for repo in kernel_repos:
    repos[repo] = groups_for_repo(repo, extra=["kernel-extra", "notdefault"])

file = open("aosp-minimal.xml", "w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"aosp\"\n")
file.write("           fetch=\"https://android.googlesource.com\" />\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"aosp\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

for repo in sorted(repos):
    # remove an unavailable repository
    if repo == "platform/packages/apps/OMA-DM":
        continue

    line = "name=\"" + repo + "\""

    # Would we get a path conflict?
    if any(s.startswith(repo + "/") for s in repos):
        line += " path=\"" + repo + ".git\""

    # Add groups
    groups = repos[repo]
    if len(groups) > 0:
        line += " groups=\"" + ",".join(groups) + "\""

    file.write("  <project " + line + " />\n")

file.write("</manifest>\n")
file.close()
