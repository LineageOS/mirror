# LineageOS Mirror Manifest

Usage: `repo init -u https://github.com/LineageOS/mirror --mirror`

Once the mirror is synced you can then run `repo init -u /path/to/mirror/LineageOS/android.git -b $BRANCHNAME` and sync normally.

If you want to sync the source quickly but want it to be up-to-date without syncing the mirror every time, then run `repo init -u http://www.github.com/LineageOS/android -b $BRANCHNAME --reference=/path/to/mirror/`. This will init the new repo and fetch all the (available) data from the mirror, but will fallback to GitHub if something is missing in the mirror.

To update the mirror, either edit the manifest manually or use the `mirror-regen.py` script.  
Please make sure you set the environment variables before using the script:

`GHUSER` contains a valid GitHub Username and  
`GHTOKEN` contains a matching GitHub Personal Access Token  
  
To set them, run the following commands in the Terminal which will run the python file:  
  
`export GHUSER="<Your Username>"`  
`export GHTOKEN="<Your Token>"` (Get one from [here](https://github.com/settings/tokens))

**WARNING:** Please make sure no repositories have been removed before pushing to Gerrit. A poor network connection could cause an incomplete manifest.
