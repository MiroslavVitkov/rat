# rat
RAm-only chaT. Inspectable code and industry standard encryption.

How to use
---
    git clone git@github.com:MiroslavVitkov/rat.git
    pip install -r rat/python/requirements.txt
    alias rat="$PWD/rat/python/rat.py"
    rat --help
    rat generate
    rat connect 87.121.47.253  # A chatroom that is supposed to be always up.


Inspectable code
---
Linux is open source yet have YOU read all the 21109354LOC (as of date of writing this)?
Has anyone you know?
Although this project relies on many libraries, the project-exclusive code strives to be concise and readable even to a beginner.


Encryption
---
Asymmetric cryptography is proven uncrackeble by brute force.
All messages are transmitted encrypted and are secure if the two endpoints are not compromised.
Disclaimer: this application was not implemented by a cryptographer.
Disclaimer: unlike WhatsApp, a compromise of a private key enables an attacker to decrypt all past messages.


Privacy
---
No 'last seen', no user broadcast or discovery, no central server, no files on the hard disk by default.

Scriptable
---
Adhering to the linux design guidelines, the program output is easily parsable by command-line tools.


Scripting
---
The client is interactive (the binary keeps on running between commands).
However, it is intended to be machine understandable.
Just capture stdout and stderr and parse them; synthetyse commands for stdin.


Tested On
---
- arch
- debian
- raspbian
- mint
- ububtu


Development Notes
---
To exclude conf.ini from staging run  
`echo 'conf.ini' >> .git/info/exclude`  
`git update-index --assume-unchanged conf.ini`  


Branching Model
---
Releases are tags in `master`.
Only QA are allowed to make those.
In the unlikely event of backporting fixes to a release, a branch is created and QA work with dev to advance the tag pointer.

All commits to `master` are smoke tested.
Those can be merge commits for anything complex at all or single commits for simple bugfixes.

Inactive feature branches are reaped monthly - there is no persistent branch beyond `master`.

The python implementation is the spec.
Any change to that is supposed to bring along chagnges in all the others.
If not, do indicate in the commit message very clearly why.
