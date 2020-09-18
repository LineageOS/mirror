#!/usr/bin/env python3

import os
import xml.etree.ElementTree as ET

try:
    import git
except ImportError:
    print("Please install the GitPython package via pip3")
    exit(1)

# Clone (or update) the repository
if os.path.isdir("aosp_manifest"):
    print("Updating aosp_manifest repository...")
    aosp_manifest = git.Repo("aosp_manifest")
    aosp_manifest.remote("origin").fetch()
else:
    print("Downloading aosp_manifest repository...")
    aosp_manifest = git.Repo.clone_from("https://android.googlesource.com/platform/manifest", "aosp_manifest")

# Get all the refs
refs = [tag for tag in sorted(aosp_manifest.git.tag(l=True).splitlines())]  # All the tags...
refs.append('origin/master')  # ...and master

repos = set()

# Look for repo names in each ref
for index, ref in enumerate(refs):
    print("[{}/{}] Parsing `{}`...".format(index + 1, len(refs), ref))

    # Load the XML
    manifest_xml = ET.fromstring(aosp_manifest.git.show("{}:default.xml".format(ref)))

    for child in manifest_xml:
        # Skip all non-project tags
        if child.tag != "project":
            continue

        repos.add(child.attrib["name"])


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

    file.write("  <project " + line + " />\n")

file.write("</manifest>\n")
file.close()
