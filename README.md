# LineageOS Mirror Manifest

Usage: `repo init -u https://github.com/LineageOS/mirror --mirror`

Once the mirror is synced you can then run `repo init -u /path/to/mirror/LineageOS/android.git -b $BRANCHNAME` and sync normally.

If you want to sync the source quickly but want it to be up-to-date without syncing the mirror every time, then run `repo init -u http://www.github.com/LineageOS/android -b $BRANCHNAME --reference=/path/to/mirror/`. This will init the new repo and fetch all the (available) data from the mirror, but will fallback to GitHub if something is missing in the mirror.

To update the mirror, either edit the manifest manually or use the `mirror-regen.py` script.  
Please make sure you set the environment variables before using the script:

`GHUSER` contains a valid GitHub Username and  
`GHTOKEN` contains a matching GitHub Personal Access Token

**WARNING:** It is possible that the download of a page fails. As a result, these repositories that were on that page will be missing in the mirror manifest. **Please double check the resulting manifest before submitting it to Gerrit**
