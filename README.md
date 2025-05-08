# rat
RAm-only chaT. Messaging utility intended to leave little trace.


Warning
---
This app has neither been designed nor inspected by a cryptographer.
It's a hobby project aimed as portable command line chat.
It makes strides for confidentiality and privacy but those are merely educational.


How to use
---
    git clone git@github.com:MiroslavVitkov/rat.git
    pip install -r rat/python/requirements.txt
    alias rat="$PWD/rat/python/rat.py"
    rat help
    rat generate
    rat listen  # this blocks, open another terminal
    rat say localhost hi bryh, wazzzup!?  # talk to yourself


Inspectable code
---
Linux is open source yet have YOU read all the 21109354LOC (as of date of writing this)?
Has anyone you know?
Although this project relies on many libraries, the project-exclusive code strives to be concise and readable even to a beginner.


Encryption
---
As long as neither private key has leaked, nothing can be cracked.
Hopefully soon we'll have forward secrecy meaning no past conversation is vulnerable.


Modes of Use
---
 - `git` style `rat say John hey there moron` non-interactive chat
 - classical interactive chat
 - chatroom host
 - artificial entities(bots e.g. chat history)


Authentication
---
The private key is Your digital identity.
A single or multiple `rat` instances can run simultaneously with different keys.
Any number of devices or instances using the same key is assumed to be a singular logical entity.


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
Any change to that is supposed to bring along changes in all the others.
If not, do indicate in the commit message very clearly why.


Architecture
---
Three layers.
Only rule so far is 'never access higher layers'.

rat - interact with outside world  
protocol - group tasks into algorithms  
bot, conf, crypto, sock, video - do specific tasks  


License
---
Code - MIT - do whatever with it, sell it if You will.
Images - chatGPT - I have full right to use even for commerial purposes.
Parsedown.php - https://github.com/erusev/parsedown
Icon - https://www.iconarchive.com/
