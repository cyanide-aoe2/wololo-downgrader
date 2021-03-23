# wololo-downgrader

![GitHub All Releases](https://img.shields.io/github/downloads/cyanide-aoe2/wololo-downgrader/total?style=plastic)

**This is the Wololo Downgrader tool.**

 Homepage: <a href="https://cyanide-aoe2.github.io/wololo-downgrader">https://cyanide-aoe2.github.io/wololo-downgrader</a><br>
 Releases: <a href="https://github.com/cyanide-aoe2/wololo-downgrader/releases">https://github.com/cyanide-aoe2/wololo-downgrader/releases</a>

**UPDATE:** I've received a report from a user that the downgrader is being flagged as malware by Windows Defender - Trojan:Win32/Fuerboos.E!cl. This seems to be related to the usage of PyInstaller which is being used to generate the .exe file from the Python Scripts. As there have been no changes to the code in the repository, users should feel free to keep using the downgrader without any worries. For future versions, I will be using a different packaging method and signing the binaries so that these issues do not arise. **Thanks for the report, jwp!**


<b>This downgrader is licensed as Beerware.</b>

The downgrader uses <a href="https://github.com/SteamRE/DepotDownloader"><b>SteamREs 
DepotDownloader</b></a> to download the files. It has been bundled with this tool to save you time
 and effort.
 
The downgrader also needs your Steam username and password to download the files. 
It does not store them anywhere. The DepotDownloader stores the authentication cookie so you 
don't need to enter your Steam 2FA code repeatedly.

The downgrader is like an unattended cigarette lighter you found somewhere. I don't care what you do with it or if it sets you or 
your computer on fire.

Updates to the downgrade files will usually be taken care of automatically. For every new game patch/update, the tool will only need a few text files to figure out what needs to be done. If this tool has an actual update, you will be informed.

The tool is only intended to be used to downgrade your personal copy of Age of Empires 2 DE so you can view replays recorded on previous versions. If you get banned, sued, shot, whatever, I'm not responsible.

If the downgrader fails, you might be missing <a href="https://dotnet.microsoft.com/download/dotnet-core/current/runtime"><b>Microsoft Dotnet Runtime Core.</b></a> Download it, Install it, Restart your computer. Try again.

Built without care in two days using Python and PyQt5. Compiled for release using pyinstaller.

<a href="https://www.buymeacoffee.com/cyanide"><b>Buy me a beer if you found this tool useful</b></a>
