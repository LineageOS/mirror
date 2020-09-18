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

# Get all the commits that we want to check
commits = set([tag.commit for tag in aosp_manifest.tags])  # All the tags...
commits.add(aosp_manifest.commit('origin/master'))  # ...and master

repos = set()

# Look for repo names in each commit
for commit in commits:
    print("Checking out `{}`...".format(commit.name_rev))
    aosp_manifest.git.checkout(commit.hexsha)

    # Load the XML
    manifest_xml = ET.parse("aosp_manifest/default.xml")
    manifest_xml_root = manifest_xml.getroot()

    for child in manifest_xml_root:
        # Skip all non-project tags
        if child.tag != "project":
            continue

        repos.add(child.attrib["name"])


file = open("aosp.xml", "w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"aosp\"\n")
file.write("           fetch=\"android.googlesource.com\" />\n")
file.write("\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"aosp\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

for repo in sorted(repos):
    file.write("  <project name=\"" + repo + "\" />\n")

file.write("</manifest>\n")
file.close()
