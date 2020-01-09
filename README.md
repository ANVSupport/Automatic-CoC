# SafeGuard-CoC
Automatically preform Most of the CoC checks for SafeGuard Installations.. 
Some of them have to be preformed manually for now
to run the script one-liner style, run the following:
```shellscript
wget -qO- https://raw.githubusercontent.com/ANVSupport/Automatic-CoC/master/shellWrapper.sh | bash --
```
## Running this script For Safeguard Machines
```shellscript
wget -qO- https://raw.githubusercontent.com/ANVSupport/Automatic-CoC/master/shellWrapper.sh | bash -- --type SG
```
To run the script first clone the repo, then run 
```shellscript
python3 main.py
```
Feature Roadmap:
- Integration with Safeguard-installer script
- create bash file that installs Python and calls the script
- prompt user to preform manual checks and log into the report
- make the app list call from a json file (instead of a hard coded dict)
