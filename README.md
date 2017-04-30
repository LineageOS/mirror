#LineageOS Mirror Manifest

Usage: `repo init -u http://github.com/LineageOS/mirror --mirror`

Once the mirror is synced you can then run `repo init -u /path/to/mirror/LineageOS/android.git -b $BRANCHNAME` and sync normally.

If you want to sync the source quickly but want it to be up-to-date without syncing the mirror every time, then run `repo init -u http://www.github.com/LineageOS/android -b $BRANCHNAME --reference=/path/to/mirror/`. This will init the new repo and fetch all the (available) data from the mirror, but will fallback to GitHub if something is missing in the mirror.

To update the mirror, either edit the manifest manually or use the `manifest-regen.sh` script. **WARNING:** The script causes a data usage of ~15 MB. Also, it is possible that it fails downloading a page of repositories that will be missing in the mirror manifest. **Please double check the resulting manifest before submitting it to Gerrit**
