import sys
import os
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtWidgets import QMainWindow, QAction, QFileDialog, QApplication
from pathlib import Path
from MainWindow import Ui_MainWindow
import fileinfo
import distutils
import shutil
import requests
from distutils import dir_util
versions = []
currentBuild = ''
latestBuild = ''
requiredBuild = ''
operation = 0
commands = []
filelists = []


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
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

    def initialise(self):
        self.populateVersionList()
        self.browseButton.clicked.connect(self.openfile)
        self.upgradeButton.clicked.connect(self.prepareUpgrade)
        self.downgradeButton.clicked.connect(self.prepareDowngrade)
        self.performOperation.clicked.connect(self.perform)
        self.performOperation.setVisible(False)
        self.downgradeButton.setVisible(False)
        self.upgradeButton.setVisible(False)
        self.steamUsername.setVisible(False)
        self.steamPassword.setVisible(False)
        self.steamPassword.setEchoMode(QtWidgets.QLineEdit.Password)
        self.label.setVisible(False)
        self.label_2.setVisible(False)
        self.versionLabel.setVisible(False)
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
                    'Built without care in two days using Python and PyQt5. Compiled for release using .<br><br>'
                    '<a href="https://www.buymeacoffee.com/cyanide"><b>Buy me a beer if you found this tool useful</b></a>')

        msg.setWindowTitle("Wololo Downgrader")
        msg.exec_()
        with open('version.txt') as version:
            current_version = int(version.read())
            print(current_version)
            url = 'https://gitcdn.link/repo/cyanide-aoe2/wololo-downgrader/master/version.txt'
            latest_version = int(requests.get(url).content)
            if latest_version > current_version:
                update = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setTextFormat(QtCore.Qt.RichText)
                msg.setText('Update available for the tool. Download it from:<br>'
                            '<a href="https://cyanide-aoe2.github.io/wololo-downgrader/">https://cyanide-aoe2.github.io/wololo-downgrader/</a>')
                msg.exec_()

    def populateVersionList(self):
        # get the latest versionlist.json file (which has the details for every game update)
        url = 'https://gitcdn.link/repo/cyanide-aoe2/wololo-downgrader/master/versionlist.json'
        versionListFile = requests.get(url)
        self.versions = versionListFile.json()

        if len(self.versions) > 0:
            self.versions.reverse()
            for each_version in self.versions:
                self.versionList.addItem(str(each_version['build']))

    def perform(self):
        if self.operation == 1: # Downgrade
            for each_command in self.commands:
                output = os.system(each_command)
            self.performBackup()

        src = ''
        with open('gamepath.txt') as gamepath:
            src = gamepath.read()[:-12]
        src += 'dgtool/' + self.requiredBuild
        dst = ''
        with open('gamepath.txt') as gamepath:
            dst = gamepath.read()[:-12]
        print(src)
        print(dst)
        a = distutils.dir_util.copy_tree(src, dst)

        msg = QtWidgets.QMessageBox()
        msg.setInformativeText('Files copied successfully. The tool will now close. To upgrade/downgrade further, start it again.')
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setWindowTitle(" ")
        msg.exec_()

        exit(0)

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
                        shutil.copy2(srcfiles[i],dstfiles[i])
                    except:
                        print(srcfiles[i] + ' unavailable most probably. skipping')
                    i += 1

        msg = QtWidgets.QMessageBox()
        msg.setInformativeText('Files backed up successfully. Downgrading will now begin.')
        msg.setWindowTitle(" ")
        msg.exec_()
        return

    def prepareUpgrade(self):
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
        self.requiredBuild = str(self.versions[idx - 1]['build'])

        src = ''
        with open('gamepath.txt') as gamepath:
            src = gamepath.read()[:-12]
            src += 'dgtool/' + self.requiredBuild
        if not os.path.isdir(src):
            print('backup unavailable. cannot upgrade')
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
                    command = 'start /wait cmd /c dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild + '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                    self.commands.append(command)
                else:
                    print('skipping uhd files')
            else:
                self.filelists.append(file_path + depot + '.txt')
                command = 'start /wait cmd /c dotnet third-party/depotdownloader/DepotDownloader.dll -app 813780 -depot ' + depot + ' -manifest ' + manifest + ' -filelist ' + file_path + depot + '.txt -dir "' + dst + 'dgtool/' + self.requiredBuild +  '/" -username ' + self.steamUsername.text() + ' -password ' + self.steamPassword.text() + ' -remember-password'
                self.commands.append(command)
        self.operation = 1  # Downgrade
        self.performOperation.setVisible(True)

    def openfile(self):
        self.downgradeButton.setVisible(False)
        self.upgradeButton.setVisible(False)
        try:
            with open('gamepath.txt') as gamepath:
                path = gamepath.read()
        except:
            path = str(Path.home())
        aoe2exe = QFileDialog.getOpenFileName(self, "Open File", path,"AoE2DE Executable (AoE2DE_s.exe)")[0]
        if aoe2exe:
            with open('gamepath.txt', 'w') as gamepath:
                gamepath.write(aoe2exe)
            propgen = fileinfo.property_sets(aoe2exe)
            for name, properties in propgen:
                for k,v in properties.items():
                    if(k == '0x4'):
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
                            self.label.setVisible(True)
                            self.label_2.setVisible(True)
                            self.steamUsername.setVisible(True)
                            self.steamPassword.setVisible(True)
                        if idx > 0:
                            self.upgradeButton.setVisible(True)
                            self.upgradeButton.setText('Upgrade to ' + str(self.versions[idx -1]['build']))
                            self.label.setVisible(True)
                            self.label_2.setVisible(True)
                            self.steamUsername.setVisible(True)
                            self.steamPassword.setVisible(True)


app = QtWidgets.QApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()