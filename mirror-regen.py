#!/usr/bin/python3

import os
import sys
try:
    from github import Github
except ImportError:
    print("Please install the pygithub package via pip3")
    exit(1)
e = os.environ.copy()
# Environment variables for github username and api token
try:
    u = e["GHUSER"]
    p = e["GHTOKEN"]
except KeyError:
    print("Please set the GHUSER and GHTOKEN environment variables")
    exit(1)

orgName = "LineageOS"
org = Github(u, p).get_user(orgName)

file = open("default.xml","w")
file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
file.write("<manifest>\n")
file.write("\n")
file.write("  <remote  name=\"github\"\n")
file.write("           fetch=\"..\" />\n")
file.write("\n")
file.write("  <default revision=\"master\"\n")
file.write("           remote=\"github\"\n")
file.write("           sync-j=\"4\" />\n")
file.write("\n")

for repo in org.get_repos():
  file.write("  <project name=\"" + repo.full_name + "\" />\n")

file.write("</manifest>\n")
file.close()
