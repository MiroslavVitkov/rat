# rat
RAm-only chaT. Inspectable code and industry standard encryption.

How to use
---
git clone git@github.com:MiroslavVitkov/rat.git
pip install -r rat/requirements.txt
alias rat="$PWD/rat/python/rat.py"
rat --help


Inspectable code
---
Linux is open source yet have YOU read all the 21109354LOC (as of date of writing this)?
Has anyone you know?
Although this project relies on many libraries, the project-exclusive code strives to be concise and readable even to a beginner.


Encription
---
Asymetric criptography is provenly uncrackeble by brute force.
All messages are transmited encrypted and are secure if the two endpoints are not compromised.
Disclaimer: this application was not implemented by a cryptographer.
Disclaimer: unlike WhatsApp, a compromise of a private key enables an attacker to decrypt all past messages.


Privacy
---
No 'last seen', no user broadcast or discovery, no central server, no files on the hard disk by default.

Scriptable
---
Adhering to the linux design guidelines, the program output is easily parsable by command-line tools.


Usage example
---
miro@general-> hi  
ruzhka@lqlq<- heya


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
