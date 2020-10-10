#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET

# Checks what file should be checked for that specific revision
# None means invalid, everything else is treated as a file name without .xml
def manifest_for_ref(ref):
    # Assume that android- tags are from AOSP
    if ref.startswith("android-") or ref in aosp_refs:
        return None

    # "Empty" tag
    if ref == "M7630AABBQVLZA0020":
        return None

    # Only default.xml was updated
    if ref == "M7201JSDCBALYA6375":
        return "default"

    if ref.startswith("AU_LINUX_ANDROID_"):
        return "caf_{}".format(ref)

    return ref

def groups_for_repo(repo):
    groups = set()

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


try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repository
if os.path.isdir("caf_manifest"):
    print("Updating caf_manifest repository...")
    caf_manifest = git.Repo("caf_manifest")
    caf_manifest.remote("origin").fetch()
else:
    print("Downloading caf_manifest repository...")
    caf_manifest = git.Repo.clone_from("https://source.codeaurora.org/quic/la/platform/manifest", "caf_manifest")

# Use AOSP repository for filtering AOSP tags
if os.path.isdir("aosp_manifest"):
    print("Updating aosp_manifest repository...")
    aosp_manifest = git.Repo("aosp_manifest")
    aosp_manifest.remote("origin").fetch()
else:
    print("Downloading aosp_manifest repository...")
    aosp_manifest = git.Repo.clone_from("https://android.googlesource.com/platform/manifest", "aosp_manifest")

# Get all the refs
refs = [tag for tag in sorted(caf_manifest.git.tag(l=True).splitlines())]  # All the tags...

aosp_refs = [tag for tag in sorted(aosp_manifest.git.tag(l=True).splitlines())]

repos = set()

# Look for repo names in each ref
for index, ref in enumerate(refs, 1):
    print("[{}/{}] Parsing `{}`...".format(index, len(refs), ref))

    manifest = manifest_for_ref(ref)

    if manifest is None:
        continue

    # Load the XML
    manifest_xml = ET.fromstring(caf_manifest.git.show("{}:{}.xml".format(ref, manifest)))

    for child in manifest_xml:
        # Skip all non-project tags
        if child.tag != "project":
            continue

        repos.add(child.attrib["name"])


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
    line = "name=\"" + repo + "\""

    # Would we get a path conflict?
    if any(s.startswith(repo + "/") for s in repos):
        line += " path=\"" + repo + ".git\""

    # Add groups
    groups = groups_for_repo(repo)
    if len(groups) > 0:
        line += " groups=\"" + ",".join(groups) + "\""

    file.write("  <project " + line + " />\n")

file.write("</manifest>\n")
file.close()
