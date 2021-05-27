# Typt - Type and encrypt

Typt is a secure raw text editor that save text encrypted with the symetrical algorithm AES-256-CBC. You can open multiple files at the same tab, in multiple tabs. Drag and drop a file in the editor open it in a new tab.

## Requirements

To run the python script, you need to have :

* [Python3](https://www.python.org/downloads/)
* [PyQt5](https://pypi.org/project/PyQt5/)

Else you should be able to run the software by downloading the build version for your OS (Linux or Windows, compiled with pyinstaller or auto-py-to-exe) in [releases](https://github.com/lasercata/Typt/releases).


## Installing
You can download directly the source code, or the last release, as you prefer. If you don't want to download Python3 and PyQt5, you can download the last release zip file that contain a build version for your OS (Windows or Linux).

### Source code
Download or clone the repository :

```bash
git clone https://github.com/lasercata/Typt.git
```

Make the launchers executable :

```bash
cd Typt
chmod +x *.py
```

### Release
Go to [releases](https://github.com/lasercata/Typt/releases), and download the zip file for your OS. Then unzip it.


## Running
In the main directory, run `./Typt_gui.py` to run the python script. Else you can run `./Typt_gui` for Linux build, or `Typt_gui.exe` for Windows build.

To open file from command line, run `./Typt_gui.py [files...]`. For command line help, type `./Typt_gui.py -h`. Show version : `./Typt_gui.py -v`.


## Authors

* **Lasercata** - [Lasercata](https://github.com/lasercata)
* **Elerias** - [Elerias](https://github.com/EleriasQueflunn) for the implementation of AES


## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details
