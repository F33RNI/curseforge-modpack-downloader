# 🟧 curseforge-modpack-downloader

## Simple zero-dependency Python script for downloading and updating CurseForge modpacks

> This program allows you to download and **update** existing mod packs (ex. for Minecraft)

----------

## 🏗️ Get started

### Download from releases

<https://github.com/F33RNI/LlM-Api-Open/releases/latest>

### Build using PyInstaller

```shell
# Clone repo
git clone https://github.com/F33RNI/curseforge-modpack-downloader
cd curseforge-modpack-downloader

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install PyInstaller
pip install pyinstaller


# Build
pyinstaller main.spec
```

> Builded file will be inside `dist` directory

### Run as python script

```shell
# Clone repo
git clone https://github.com/F33RNI/curseforge-modpack-downloader
cd curseforge-modpack-downloader

# Run script
python main.py -h
```

----------

## 📃 Usage

```text
usage: curseforge-modpack-downloader [-h] [--user-agent USER_AGENT] [-s | -r | -o] [-v] zip_path_or_url destination_dir

Simple zero-dependency Python script for downloading and updating CurseForge modpacks

positional arguments:
  zip_path_or_url       Path to downloaded modpack zip-file or direct URL to download
  destination_dir       destination path (ex. /home/username/.minecraft/versions/MyModPack/)

options:
  -h, --help            show this help message and exit
  --user-agent USER_AGENT
                        user agent for https://api.cfwidget.com/{project_id} (default: Mozilla/5.0 (Windows NT 10.0;
                        Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36)
  -s, --skip            automatically skip existing extra files without overwriting them (default: ask user)
  -r, --rename          automatically rename existing extra files into .old without overwriting them (default: ask
                        user)
  -o, --overwrite       automatically overwrite existing extra files (default: ask user)
  -v, --version         show program's version number and exit
```

----------

## 📝 Example

> Replace <https://www.curseforge.com/api/v1/mods/123456/files/1234567/download> with actual direct download link. You can get it by right-clinking on "If your download didn’t start, **try again**" and copying link into clipboard

```shell
$ dist/curseforge-modpack-downloader-linux-x86_64-1.0.0 https://www.curseforge.com/api/v1/mods/123456/files/1234567/download /home/test/.minecraft/versions/MyTestModPack
[2024-04-24 21:44:26,354] [INFO] [main] curseforge-modpack-downloader v1.0.0
[2024-04-24 21:44:26,354] [INFO] [main] https://github.com/F33RNI/curseforge-modpack-downloader
[2024-04-24 21:44:26,354] [INFO] [main] Working directory: /tmp/tmpqlzg847a
[2024-04-24 21:44:26,354] [INFO] [open_or_download] Downloading https://www.curseforge.com/api/v1/mods/123456/files/1234567/download
[2024-04-24 21:44:28,328] [INFO] [unzip_modpack] Extracting archive
[2024-04-24 21:44:28,601] [INFO] [unzip_modpack] Trying to read and parse manifest.json
[2024-04-24 21:44:28,601] [INFO] [unzip_modpack] Found 123 files
[2024-04-24 21:44:28,602] [INFO] [main] Copying manifest.json
[2024-04-24 21:44:28,602] [INFO] [main] Copying modlist.html
[2024-04-24 21:44:28,603] [INFO] [main] [1/123] Retrieving project information from https://api.cfwidget.com/123456
[2024-04-24 21:44:29,129] [INFO] [main] [1/123] File Mod1-1.2.3-1.2.3-forge.jar already exists
...
[2024-04-24 21:45:48,715] [INFO] [main] [10/123] Retrieving project information from https://api.cfwidget.com/234567
[2024-04-24 21:45:49,198] [INFO] [main] [10/123] Downloading https://www.curseforge.com/api/v1/mods/234567/files/8901234/download as Mod2-1.2.3-1.2.3.jar
[2024-04-24 21:45:50,790] [WARNING] [main] [10/123] Deleting previous version Mod2-1.2.2-1.2.3.jar
...
[2024-04-24 21:46:04,703] [INFO] [main] Skipping file default-server.properties. Already exists
...
[2024-04-24 21:52:08,518] [WARNING] [main] Your config/test.properties is different from the downloaded one. Please select what to do

Difference:
---
+++
@@ -1,2 +1,2 @@
-test=test1
+test=test2

[s]kip - keep your version | [o]verwrite - replace with downloaded | [r]ename old file by adding .old | [e]xit - cancel and exit (press s, o, r or e): s
[2024-04-24 21:53:54,777] [INFO] [main] Skipping file config/test.properties
...
[2024-04-24 21:56:35,511] [INFO] [main] Downloading https://maven.minecraftforge.net/net/minecraftforge/forge/1.2.3-1.2.3/forge-1.2.3-1.2.3-installer.jar as /home/test/.minecraft/versions/DeceasedCraft/forge-1.2.3-1.2.3-installer.jar
[2024-04-24 21:56:36,862] [INFO] [main] Forge 1.2.3 downloaded. Please run java -jar "/home/test/.minecraft/versions/DeceasedCraft/forge-1.2.3-1.2.3-installer.jar" to install client and use --installServer argument to install server
[2024-04-24 21:56:36,863] [INFO] [main] MyTestModPack v1.2.3 downloaded
[2024-04-24 21:56:36,863] [INFO] [main] curseforge-modpack-downloader finished
```

----------

## ✨ Contribution

- Anyone can contribute! Just create a pull request
