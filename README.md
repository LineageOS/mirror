#LineageOS Mirror Manifest

Usage: `repo init -u http://github.com/LineageOS/mirror --mirror`

Once the mirror is synced you can then run `repo init -u /path/to/mirror/LineageOS/android.git -b $BRANCHNAME` and sync normally.

If you want to sync the source fast but want it to be up-to-date without syncing the mirror every time, then run `repo init -u http://www.github.com/LineageOS/android -b $BRANCHNAME --reference=/path/to/mirror/`. This will init the new repo and copy every data it needs from the mirror when it is synced and will fallback to GitHub, if something is missing in the mirror.


###WARNING:
Things will break if you do something like this:
`repo init -u http://www.github.com/LineageOS/mirror --reference=/path/to/other/mirror/ --mirror`

This will cause repo to fail due to "Couldn't find remote ref refs/heads/master".
Specifying the master branch to fetch all branches works when fetching from the server, but it does NOT seem to work when using ANY reference.
