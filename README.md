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
    rat generate
    rat say rat.pm Just _any_ random string.

If this completes without errors then Your installation is sane.
Nothing responds yet.


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
 - p2p - rat listen/say - requires a public IP and punching a port in firewalls and routers
 - chatroom - rat relay/share - have a central server retransmit messages voids the IP requirement
 - phonebook - rat serve/ask - searchable nameserver


Digital Identity
---
RAT is more than a chat app, it's a trust platform.
An 'entity' is defined by the following factors in descending order of importance:
  - possesses the private key,
  - device fingerprint already authorized from another trusted one <not implemented yet>,
  - other users have vouched <not implemented yet>.

This enables one to share huge encrypted files(petabytes) or VoIP<not implemented yet>.
Any number of devices or instances using the same key is assumed to be a singular logical entity.


Development Notes
---
To exclude conf.ini from staging run  
`echo 'conf.ini' >> .git/info/exclude`  
`git update-index --assume-unchanged conf.ini`  

Keywords throughout code comments:
  - `todo:` - nice to have
  - `warn:` - probably hiding a bug


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

Panic plan is to `git switch master && git branch save && git reset --hard <last tag>`.


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


Legal
---
Running an instance of 'rat relay' can enable various illegal activities e.g. inciting to violence, child porn videos and more.
Whoever hosts the chatroom(relay) is probably liable in their respective jurisdiction.
RAT is committed to solving that through 'bots'.
