#!/usr/bin/env python3

import os
import re
import sys
import xml.etree.ElementTree as ET

KERNEL_MANIFEST = "kernel/manifest"


try:
    import git
except ImportError:
    sys.exit("Please install the GitPython package via pip3")

# Clone (or update) the repository
if os.path.isdir("aosp_kernel_manifest"):
    print("Updating kernel_manifest repository...")
    kernel_manifest = git.Repo("aosp_kernel_manifest")
    kernel_manifest.remote("origin").fetch()
else:
    print("Downloading aosp_kernel_manifest repository...")
    kernel_manifest = git.Repo.clone_from("https://android.googlesource.com/kernel/manifest", "aosp_kernel_manifest")

# Get all the refs
refs = [h.name for h in kernel_manifest.refs]  # All the refs, repo only has branches no tags...

repos = set()

# Look for repo names in each ref
for index, ref in enumerate(refs, 1):
    # Skip broken refs
    if ref == "origin/android-gs-raviole-mainline":
        continue
    print("[{}/{}] Parsing `{}`...".format(index, len(refs), ref))

    # Load the XML
    manifest_xml = ET.fromstring(kernel_manifest.git.show("{}:default.xml".format(ref)))

    for child in manifest_xml:
        # Skip all non-project tags
        if child.tag != "project":
            continue

        repos.add(child.attrib["name"])


file = open("aosp-kernel.xml", "w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"aosp\"\n")
file.write("           fetch=\"https://android.googlesource.com\" />\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"aosp\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

# Always add kernel/manifest so one can sync from this manifest
if KERNEL_MANIFEST not in repos:
    repos.add(KERNEL_MANIFEST)

for repo in sorted(repos):
    line = "name=\"" + repo + "\""

    # Would we get a path conflict?
    if any(s.startswith(repo + "/") for s in repos):
        line += " path=\"" + repo + ".git\""

    file.write("  <project " + line + " />\n")

file.write("</manifest>\n")
file.close()
