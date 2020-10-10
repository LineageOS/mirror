#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET

# Checks what file should be checked for that specific revision
def manifest_for_ref(ref):
    # Only default.xml was updated
    if ref == "M7201JSDCBALYA6375":
        return "default"

    if ref.startswith("AU_LINUX_ANDROID_") or ref.startswith("AU_LINUX_KERNEL."):
        return "caf_{}".format(ref)

    return ref

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
        print("\033[K[{}/{}] Parsing `{}`...".format(index, len(refs), ref), end='\r')

        manifest_name = manifest_for_ref(ref)

        if manifest_name is None:
            continue

        # Load the XML
        manifest_xml = ET.fromstring(manifest.git.show("{}:{}.xml".format(ref, manifest_name)))

        # Check for the correct remote
        for remote in manifest_xml.findall('remote'):
            if remote.attrib["fetch"] == "https://source.codeaurora.org/quic/la/":
                break
        else:
            # This runs if no break has been encountered
            continue

        for child in manifest_xml.findall('project'):
            # Filter remaining quic/ repos
            if child.attrib["name"].startswith("quic/"):
                continue

            repos.add(child.attrib["name"])

    return repos


try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repositories
# Use AOSP repository for filtering AOSP tags
platform_manifest = get_git_repo("https://source.codeaurora.org/quic/la/platform/manifest", "caf_manifest")
kernel_manifest = get_git_repo("https://source.codeaurora.org/quic/la/kernelplatform/manifest", "caf_kernel_manifest")
aosp_manifest = get_git_repo("https://android.googlesource.com/platform/manifest", "aosp_manifest")

# Get all the refs
platform_refs = [tag for tag in sorted(platform_manifest.git.tag(l=True).splitlines())]
kernel_refs = [tag for tag in sorted(kernel_manifest.git.tag(l=True).splitlines())]
aosp_refs = [tag for tag in sorted(aosp_manifest.git.tag(l=True).splitlines())]

# Exclude refs found on AOSP (assume that `android-*` is also from there)
platform_refs = [ref for ref in platform_refs if not ref.startswith("android-") and ref not in aosp_refs]

# Skip a broken ref
platform_refs.remove("M7630AABBQVLZA0020")

# Look for repo names in each ref
platform_repos = parse_all_refs(platform_manifest, platform_refs)
kernel_repos = parse_all_refs(kernel_manifest, kernel_refs)

# Always add the manifest so one can sync from this mirror
platform_repos.add("platform/manifest")
kernel_repos.add("kernelplatform/manifest")

# Remove kernel repositories that are already in the platform manifest
kernel_repos = kernel_repos - platform_repos

# Generate groups for all repositories
repos = {}
for repo in platform_repos:
    repos[repo] = groups_for_repo(repo)
for repo in kernel_repos:
    repos[repo] = groups_for_repo(repo, extra=["kernel-extra", "notdefault"])

file = open("caf-minimal.xml", "w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"caf\"\n")
file.write("           fetch=\"https://source.codeaurora.org/quic/la/\" />\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"caf\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

for repo in sorted(repos):
    # Remove a few repositories
    if repo == "platform/tools/vendor/google_prebuilts/arc" or repo.startswith("platform/vendor/google_"):
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
