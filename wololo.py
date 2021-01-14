# pyinstaller -y --clean --hidden-import=win32timezone --add-data=".\third-party;third-party" --add-data=".\diffs;diffs" --add-data="version.txt;." --add-data="diffs_version.txt;." -w wololo.py
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path
from MainWindow import Ui_MainWindow
from mgz.summary import Summary
import fileinfo
import distutils
import shutil
import requests
from distutils import dir_util
import os
import sys
import wget
from zipfile import ZipFile
import json
import pexpect
import pexpect.popen_spawn


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    aoe2exe = None
    versions = []
    currentBuild = ''
    latestBuild = ''
    requiredBuild = ''
    operation = 0
    commands = []
    filelists = []
    progressbar = None
    process_queue = None

    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.initialise()
        self.currentBuild = ''
        self.latestBuild = ''
        self.requiredBuild = ''
        self.operation = 0
        self.commands = []
        self.filelists = []
        self.progressbar = QtWidgets.QProgressBar(self)
        self.progressbar.setMaximum(0)
        self.progressbar.setMinimum(0)
        self.progressbar.setValue(0)
        self.statusBar().setVisible(False)
        self.statusBar().setStyleSheet('QStatusBar::item {border: None;}')
        self.statusBar().addWidget(self.progressbar)

    def dragEnterEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        files = event.mimeData().urls()
        if len(files) > 1:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle(' ')
            msg.setTextFormat(QtCore.Qt.RichText)
            text = 'Multiple files dropped. Please drop a single file.'
            msg.setText(text)
            msg.exec_()
            return
        file = files[0].toLocalFile()
        self.statusBar().setVisible(True)
        with open(file, 'rb') as data:
            summary = Summary(data)
            if summary:
                platform = summary.get_platform()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle(' ')
                msg.setTextFormat(QtCore.Qt.RichText)
                text = 'Error reading replay file. Cannot analyse recordings against AI or from private games.'
                msg.setText(text)
                msg.exec_()
                return
            if platform:
                match_id = platform['platform_match_id']
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle(' ')
                msg.setTextFormat(QtCore.Qt.RichText)
                text = 'Error reading replay file. Cannot analyse recordings against AI or from private games.'
                msg.setText(text)
                msg.exec_()
                return
            if not match_id:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle(' ')
                msg.setTextFormat(QtCore.Qt.RichText)
                text = 'Error reading replay file. Cannot analyse recordings against AI or from private games.'
                msg.setText(text)
                msg.exec_()
                return

            url = 'https://aoe2.net/api/match?uuid=' + match_id
            output = requests.get(url)
            if output.status_code == 200:
                result = output.json()
                version = result['version']
                if version:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setWindowTitle(' ')
                    msg.setTextFormat(QtCore.Qt.RichText)
                    text = 'Replay recorded on patch version: ' + version + '.'
                    msg.setText(text)
                    msg.exec_()
                    self.statusBar().setVisible(False)
                    return
                else:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Critical)
                    msg.setWindowTitle(' ')
                    msg.setTextFormat(QtCore.Qt.RichText)
                    text = 'Error reading replay file. Cannot analyse recordings from private games.'
                    msg.setText(text)
                    msg.exec_()
                    return
            else:
                self.statusBar().setVisible(False)
                return

    def setup(self):
        self.browseButton.clicked.connect(self.openfile)
        self.upgradeButton.clicked.connect(self.prepareUpgrade)
        self.downgradeButton.clicked.connect(self.prepareDowngrade)
        self.performOperation.clicked.connect(self.perform)
        self.saveCredsCheckbox.clicked.connect(self.saveCreds)
        self.uhdCheckbox.setVisible(False)
        self.performOperation.setVisible(False)
        self.downgradeButton.setVisible(False)
        self.upgradeButton.setVisible(False)
        self.steamUsername.setVisible(False)
        self.steamPassword.setVisible(False)
        self.steamPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label.setVisible(False)
        self.label_2.setVisible(False)
        self.versionLabel.setVisible(False)
        self.saveCredsCheckbox.setVisible(False)
        self.label_6.setVisible(False)
        self.currentBuild = ''
        self.latestBuild = ''
        self.requiredBuild = ''
        self.operation = 0
        self.commands = []
        self.filelists = []
        if self.aoe2exe:
            self.browseButton.setVisible(False)
            self.openfile()

    def initialise(self):
        self.setup()
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setTextFormat(QtCore.Qt.RichText)
        msg.setText('Note:<br>'
                    'This is the Wololo Downgrader tool.<br>'
                    'Latest releases and source code will be available at: <br>'
                    '<a href="https://cyanide-aoe2.github.io/wololo-downgrader">'
                    '<b>https://cyanide-aoe2.github.io/wololo-downgrader</b></a><br><br>'
                    '<b>This tool is licensed as Beerware.</b><br><br>'
                    'The tool uses <a href="https://github.com/SteamRE/DepotDownloader"><b>SteamRE\'s '
                    'DepotDownloader</b></a> to download the files. It has been bundled with this tool to save you time'
                    ' and effort.<br><br>The tool also needs your Steam username and password to download the files. '
                    'It does not store them anywhere. The DepotDownloader stores the authentication cookie so you '
                    'don\'t need to enter your Steam 2FA code repeatedly.<br><br>This tool is like an unattended '
                    'cigarette lighter you found somewhere. I don\'t care what you do with it or if it sets you or '
                    'your computer on fire.<br><br>Updates to the downgrade files will usually be taken care of '
                    'automatically. For every new game patch/update, the tool will only need a few text files to '
                    'figure out what needs to be done. If this tool has an actual update, you will be informed.<br><br>'
                    'The tool is only intended to be used to downgrade your personal copy of Age of Empires 2 DE '
                    'so you can view replays recorded on previous versions. If you get banned, sued, shot, whatever, '
                    'I\'m not responsible.<br><br>'
                    'If the tool fails, you might be missing <a href="https://dotnet.microsoft.com/download/dotnet-core/current/runtime"><b>Microsoft Dotnet Runtime Core.</b></a> Download it, Install it, Restart your computer. Try again.<br><br>'
                    'Built without care using Python and PyQt5. Compiled for release using pyinstaller.<br><br>'
                    '<a href="https://www.buymeacoffee.com/cyanide"><b>Buy me a beer if you found this tool useful</b></a>')
        msg.setWindowTitle("Wololo Downgrader")
        msg.exec_()

        output = os.system('dotnet --list-runtimes')
        if output != 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setTextFormat(QtCore.Qt.RichText)
            msg.setText('Dotnet Core Runtime is not installed. Please download it from here: <a href="https://dotnet.microsoft.com/download/dotnet-core/current/runtime">Microsoft</a>.<br><br>'
                        'After installing, Dotnet Runtime Core, you will need to restart your computer before you can run the downgrader.')
            msg.exec_()
        with open('version.txt') as version:
            current_version = int(version.read())
            url = 'https://raw.githubusercontent.com/cyanide-aoe2/wololo-downgrader/master/version.txt'
            latest_version = int(requests.get(url).content)
            if latest_version > current_version:
                update = QtWidgets.QMessageBox()
                update.setIcon(QtWidgets.QMessageBox.Information)
                update.setTextFormat(QtCore.Qt.RichText)
                update.setText('Update available for the tool. Download it from:<br>'
                            '<a href="https://cyanide-aoe2.github.io/wololo-downgrader/">https://cyanide-aoe2.github.io/wololo-downgrader/</a>')
                update.exec_()
        with open('diffs_version.txt') as diffs_version:
            diffs_current_version = int(diffs_version.read())
            url = 'https://raw.githubusercontent.com/cyanide-aoe2/wololo-downgrader/master/diffs_version.txt'
            diffs_latest_version = int(requests.get(url).content)
            if diffs_latest_version > diffs_current_version:
                update = QtWidgets.QMessageBox()
                update.setIcon(QtWidgets.QMessageBox.Information)
                update.setTextFormat(QtCore.Qt.RichText)
                update.setText('Updated diff files available for the tool. Press OK to download the latest files.')
                update.exec_()
                url = 'https://raw.githubusercontent.com/cyanide-aoe2/wololo-downgrader/master/diffs.zip'
                fname = 'diffs' + str(diffs_latest_version) + '.zip'
                wget.download(url, fname)
                os.rename('./diffs', './diffs_old')
                with ZipFile('diffs.zip', 'r') as zip:
                    zip.extractall()

        self.populateVersionList()

    def populateVersionList(self):
        # get the latest versionlist.json file (which has the details for every game update)
        url = 'https://raw.githubusercontent.com/cyanide-aoe2/wololo-downgrader/master/versionlist.json'
        versionListFile = requests.get(url)
        self.versions = versionListFile.json()

        if len(self.versions) > 0:
            self.versions.reverse()
            for each_version in self.versions:
                self.versionList.addItem(str(each_version['build']))

    def saveCreds(self):
        if self.saveCredsCheckbox.isChecked():
            if self.steamUsername.text() and self.steamPassword.text():
                creds = {'username': self.steamUsername.text(), 'password': self.steamPassword.text()}
                with open('steam_creds.txt', 'w') as steam_creds_file:
                    json.dump(creds, steam_creds_file)
            else:
                msg = QtWidgets.QMessageBox()
                msg.setInformativeText('Credentials not entered. Cannot save.')
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setWindowTitle(" ")
                msg.exec_()
                self.saveCredsCheckbox.setChecked(False)
        else:
            if os.path.exists('./steam_creds.txt'):
                os.remove('steam_creds.txt')

    def perform(self):
        if self.operation == 1:  # Downgrade
            for each_command in self.commands:
                p = pexpect.popen_spawn.PopenSpawn(each_command, encoding="utf-8")
                p.logfile_read = sys.stdout
                responses = [
                    "result: OK",
                    "Please enter .*: ",
                    "InvalidPassword",
                    pexpect.EOF
                ]
                response = p.expect(responses)
                if response == 0:
                    print('success')
                elif response == 1:
                    steam_guard_code, ok = QtWidgets.QInputDialog.getText(self, 'Two Factor Auth',
                                                                          'Please enter your Steam Guard or Two Factor Auth code:')
                    if ok:
                        p.sendline(steam_guard_code)
                        if p.expect(responses, timeout=30) == 1:
                            print('invalid auth code')
                            return
                    else:
                        print('Two Factor Auth failed')
                elif response == 2:
                    print('wrong username or password')
                else:
                    print('received unexpected response')

                p.expect(pexpect.EOF, timeout=None)
            self.performBackup()

        src = ''
        with open('gamepath.txt') as gamepath:
            src = gamepath.read()[:-12]
        src += 'dgtool/' + self.requiredBuild
        dst = ''
        with open('gamepath.txt') as gamepath:
            dst = gamepath.read()[:-12]
        a = distutils.dir_util.copy_tree(src, dst)

        msg = QtWidgets.QMessageBox()
        msg.setInformativeText(
            'Files copied successfully. You can now upgrade/downgrade further if required, else the tool can be closed.')
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(" ")
        msg.exec_()
        self.setup()

    def performBackup(self):
        dst = ''
        with open('gamepath.txt') as gamepath:
            dst = gamepath.read()[:-12]

        srcfiles = []
        dstfiles = []
        for each_list in self.filelists:
            with open(each_list) as file_list:
                files = [line.rstrip() for line in file_list]
                for each_file in files:
                    srcfiles.append(dst + each_file)
                    dstfiles.append(dst + 'dgtool/' + self.currentBuild + '/' + each_file)

                # Create file paths for backup
                for each_dstfile in dstfiles:
                    regen = each_dstfile.split('/')
                    f = 0
                    dstfolder = ''
                    while f < len(regen) - 1:
                        dstfolder += regen[f] + '/'
                        f += 1
                    Path(dstfolder).mkdir(parents=True, exist_ok=True)

                i = 0
                while i < len(srcfiles):
                    try:
                        shutil.copy2(srcfiles[i], dstfiles[i])
                    except:
                        print(srcfiles[i] + ' not present in the previous patch. skipping')
                    i += 1

        print('Files backed up successfully. Downgrading will now begin.')
        return

    def prepareUpgrade(self):
        idx = 0
        for each_version in self.versions:
            if self.currentBuild == str(each_version['build']):
                currentItem = idx
                break
            idx += 1
        self.requiredBuild = str(self.versions[idx - 1]['build'])

        src = ''
        with open('gamepath.txt') as gamepath:
            src = gamepath.read()[:-12]
            src += 'dgtool/' + self.requiredBuild
        if not os.path.isdir(src):
            msg = QtWidgets.QMessageBox()
            msg.setText("Backup unavailable. Cannot restore. Please use Steam's Verify File Integrity feature to go back to the latest version. Future versions will support upgrading even with missing backups")
            msg.setWindowTitle("Upgrade failed")
            msg.exec_()
            return

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Upgrade operation:")
        msg.setInformativeText('Your version will be upgraded to ' + self.requiredBuild)
        msg.setWindowTitle("Upgrading")
        msg.exec_()

        self.operation = 2
        self.performOperation.setVisible(True)

    def prepareDowngrade(self):
        if self.steamUsername.text() == '' or self.steamPassword.text() == '':
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Steam credentials missing')
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        idx = 0
        for each_version in self.versions:
            if self.currentBuild == str(each_version['build']):
                currentItem = idx
                break
            idx += 1
        self.requiredBuild = str(self.versions[idx + 1]['build'])
        updated_depots = self.versions[idx]['downgrade_depots']
        self.commands = []
        self.filelists = []
        file_path = 'diffs/' + self.currentBuild + '/'

        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText("Downgrade operation:")
        msg.setInformativeText('Your version will be downgraded to ' + self.requiredBuild)
        msg.setWindowTitle("Downgrading")
        msg.exec_()

        dst = ''
        with open('gamepath.txt') as gamepath:
            dst = gamepath.read()[:-12]

        for depot, manifest in updated_depots.items():
            if depot == '1039811':
                if self.uhdCheckbox.isChecked():
                    self.filelists.append(file_path + depot + '.txt')
                    # command = 'start /wait cmd /c dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild + '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                    command = 'dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild + '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                    self.commands.append(command)
            else:
                self.filelists.append(file_path + depot + '.txt')
                # command = 'start /wait cmd /c dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild +  '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                command = 'dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild + '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                self.commands.append(command)
        self.operation = 1  # Downgrade
        self.performOperation.setVisible(True)

    def openfile(self):
        if not self.aoe2exe:
            self.downgradeButton.setVisible(False)
            self.upgradeButton.setVisible(False)
            try:
                with open('gamepath.txt') as gamepath:
                    path = gamepath.read()
            except:
                path = str(Path.home())
            self.aoe2exe = QFileDialog.getOpenFileName(self, "Open File", path, "AoE2DE Executable (AoE2DE_s.exe)")[0]
        if self.aoe2exe:
            with open('gamepath.txt', 'w') as gamepath:
                gamepath.write(self.aoe2exe)
            propgen = fileinfo.property_sets(self.aoe2exe)
            for name, properties in propgen:
                for k, v in properties.items():
                    if k == '0x4':
                        self.currentBuild = v.split('.')[2]
                        self.versionLabel.setText('Current version: ' + self.currentBuild)
                        self.versionLabel.setVisible(True)
                        idx = 0
                        for each_version in self.versions:
                            if self.currentBuild == str(each_version['build']):
                                currentItem = idx
                                break
                            idx += 1
                        self.versionList.setCurrentRow(idx)

                        if idx < len(self.versions):
                            self.downgradeButton.setVisible(True)
                            self.downgradeButton.setText('Downgrade to ' + str(self.versions[idx + 1]['build']))
                        if idx > 0:
                            self.upgradeButton.setVisible(True)
                            self.upgradeButton.setText('Upgrade to ' + str(self.versions[idx -1]['build']))
                        self.populateCreds()
                        self.label.setVisible(True)
                        self.label_2.setVisible(True)
                        self.steamUsername.setVisible(True)
                        self.steamPassword.setVisible(True)
                        self.saveCredsCheckbox.setVisible(True)
                        self.label_6.setVisible(True)
                        self.uhdCheckbox.setVisible(True)
                        self.browseButton.setVisible(False)
                        self.label_7.setVisible(False)

    def populateCreds(self):
        creds = {}
        try:
            with open('./steam_creds.txt', 'r') as steam_creds_file:
                creds = json.load(steam_creds_file)
        except:
            creds = {'username': None, 'password': None}

        if creds['username'] and creds['password']:
            self.steamUsername.setText(creds['username'])
            self.steamPassword.setText(creds['password'])
            self.saveCredsCheckbox.setChecked(True)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
