"""
Copyright (C) 2024 Fern Lane, curseforge-modpack-downloader

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
See the License for the specific language governing permissions and
limitations under the License.

IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

import argparse
from difflib import unified_diff
import glob
import hashlib
import io
import json
import logging
import os
import shutil
import tempfile
import time
from typing import Dict
from urllib import request
import zipfile

from _version import __version__
from getch import Getch

USER_AGENT_DEFAULT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
)

LOGGING_FORMATTER = "[%(asctime)s] [%(levelname)s] [%(funcName)s] %(message)s"

INFO_URL = "https://api.cfwidget.com/{project_id}"
DOWNLOAD_URL = "https://www.curseforge.com/api/v1/mods/{project_id}/files/{file_id}/download"
FORGE_URL = "https://maven.minecraftforge.net/net/minecraftforge/forge/{game_version}-{forge_version}/forge-{game_version}-{forge_version}-installer.jar"
FABRIC_URL = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/1.0.1/fabric-installer-1.0.1.jar"
FABRIC_FILE_NAME = "fabric-installer-1.0.1.jar"

MANIFEST_FILE = "manifest.json"
MODLIST_FILE = "modlist.html"

CHECKSUM_BUFFER_SIZE = 2048

FILE_DOWNLOAD_MAX_ATTEMPTS = 3


def file_md5(file_path: str) -> str:
    """Calculates MD5 checksum of file

    Args:
        file_path (str): path to file

    Returns:
        str: file's MD5 checksum as hex
    """
    md5 = hashlib.md5()
    with open(file_path, "rb") as file:
        data = file.read(CHECKSUM_BUFFER_SIZE)
        while len(data) > 0:
            md5.update(data)
            data = file.read(CHECKSUM_BUFFER_SIZE)
    return md5.hexdigest()


def file_copy(source: str, destination: str, rewrite: bool) -> None:
    """Copies source into destination

    Args:
        source (str): source file path with extension
        destination (str): destination file path with extension
        rewrite (bool): if set False, will move existing file into destination.old
    """
    try:
        # Create dirs if needed
        destination_dir = os.path.dirname(destination)
        if not os.path.exists(destination_dir):
            logging.info(f"Creating directory {destination_dir}")
            os.makedirs(destination_dir)

        if not rewrite and os.path.exists(destination):
            # Make old files even older to make sure destination.old doesn't exist
            very_old_files = sorted(glob.glob(f"{destination}.old*"), reverse=True)
            for very_old_file in very_old_files:
                logging.info(f"Renaming {very_old_file} into {very_old_file}.old")
                shutil.move(very_old_file, f"{very_old_file}.old")

            # Backup file
            logging.info(f"Renaming {destination} into {destination}.old")
            shutil.move(destination, f"{destination}.old")

        # Copy and replace if needed
        logging.info(f"Copying {source} into {destination}")
        shutil.copyfile(source, destination)
    except Exception as e:
        logging.error(f"Unable to copy {source} into {destination}. Please copy files manually", exc_info=e)


def open_or_download(zip_or_url: str, temp_dir: str) -> io.IOBase:
    """Opens provided zip file or downloads as temp file and opens it

    Args:
        zip_or_url (str): path to downloaded file or direct URL to download
        temp_dir (str): current working directory

    Returns:
        io.IOBase: opened file
    """
    # User provided existing path -> keep as is
    if os.path.exists(zip_or_url):
        return open(zip_or_url, "rb")

    # Download into temp file
    out_file = tempfile.TemporaryFile(dir=temp_dir)
    logging.info(f"Downloading {zip_or_url}")
    with request.urlopen(zip_or_url) as response:
        shutil.copyfileobj(response, out_file)
    return out_file


def unzip_modpack(archive: io.IOBase, temp_dir: str) -> Dict:
    """Unzips archive into temp_dir and parses manifest.json

    Args:
        archive (io.IOBase): opened archive file
        temp_dir (str): current working directory

    Raises:
        Exception: in case of error

    Returns:
        Dict: manifest as dictionary
    """
    logging.info("Extracting archive")
    with zipfile.ZipFile(archive, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Read and parse manifest file
    logging.info("Trying to read and parse manifest.json")
    with open(os.path.join(temp_dir, MANIFEST_FILE), "r", encoding="utf-8") as file:
        manifest = json.loads(file.read())
    if not manifest:
        raise Exception("Manifest read error")
    if "name" not in manifest:
        raise Exception('No "name" key in manifest')
    if "version" not in manifest:
        raise Exception('No "version" key in manifest')
    if "files" not in manifest:
        raise Exception('No "files" key in manifest')
    logging.info(f"Found {len(manifest['files'])} files")

    return manifest


def parse_args() -> argparse.Namespace:
    """Parses cli arguments

    Returns:
        argparse.Namespace: parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Simple zero-dependency Python script for downloading and updating CurseForge modpacks",
    )
    parser.add_argument(
        "zip_path_or_url",
        type=str,
        help="Path to downloaded modpack zip-file or direct URL to download",
    )
    parser.add_argument(
        "destination_dir",
        type=str,
        help="destination path (ex. /home/username/.minecraft/versions/MyModPack/)",
    )
    parser.add_argument(
        "--user-agent",
        type=str,
        default=USER_AGENT_DEFAULT,
        required=False,
        help=f"user agent for {INFO_URL} (default: {USER_AGENT_DEFAULT})",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s",
        "--skip",
        action="store_true",
        required=False,
        help="automatically skip existing extra files without overwriting them (default: ask user)",
    )
    group.add_argument(
        "-r",
        "--rename",
        action="store_true",
        required=False,
        help="automatically rename existing extra files into .old without overwriting them (default: ask user)",
    )
    group.add_argument(
        "-o",
        "--overwrite",
        action="store_true",
        required=False,
        help="automatically overwrite existing extra files (default: ask user)",
    )
    parser.add_argument("-v", "--version", action="version", version=__version__)
    return parser.parse_args()


def main() -> None:
    # Parse CLI args
    args = parse_args()

    # Initialize logging
    logging.basicConfig(level=logging.INFO, format=LOGGING_FORMATTER)

    # Log curseforge-modpack-downloader version and GitHub link
    logging.info(f"curseforge-modpack-downloader v{__version__}")
    logging.info("https://github.com/F33RNI/curseforge-modpack-downloader")

    # Create tempdir
    with tempfile.TemporaryDirectory() as temp_dir:
        logging.info(f"Working directory: {temp_dir}")

        try:
            ######################################
            # Extract archive and parse manifest #
            ######################################
            archive = open_or_download(args.zip_path_or_url, temp_dir)
            manifest = unzip_modpack(archive, temp_dir)

            #################################################
            # Copy and overwrite manifest and modlist files #
            #################################################
            if not os.path.exists(args.destination_dir):
                logging.info(f"Creating directory {args.destination_dir}")
                os.makedirs(args.destination_dir)
            logging.info(f"Copying {MANIFEST_FILE}")
            shutil.copyfile(os.path.join(temp_dir, MANIFEST_FILE), os.path.join(args.destination_dir, MANIFEST_FILE))
            logging.info(f"Copying {MODLIST_FILE}")
            shutil.copyfile(os.path.join(temp_dir, MODLIST_FILE), os.path.join(args.destination_dir, MODLIST_FILE))

            ##############################################
            # Iterate and download all files in manifest #
            ##############################################
            files_total = len(manifest["files"])
            for i, file in enumerate(manifest["files"]):
                project_id = file["projectID"]
                file_id = file["fileID"]

                # Get all info
                url = INFO_URL.format(project_id=project_id)
                headers = {"content-type": "application/json", "User-Agent": args.user_agent}
                logging.info(f"[{i + 1}/{files_total}] Retrieving project information from {url}")
                request_ = request.Request(url, headers=headers)
                project_info = json.loads(request.urlopen(request_).read().decode("utf-8"))
                if (
                    not project_info
                    or "title" not in project_info
                    or "type" not in project_info
                    or "files" not in project_info
                ):
                    logging.warning(
                        f"[{i + 1}/{files_total}] Unable to parse project info. Skipping project {project_id}"
                    )
                    continue

                # Convert type into directory
                type_ = project_info["type"]
                if type_ == "Mods":
                    root_dir = "mods"
                elif type_ == "Resource Packs":
                    root_dir = "resourcepacks"
                elif type_ == "Shaders":
                    root_dir = "shaderpacks"
                else:
                    root_dir = "mods"
                    logging.warning(f"[{i + 1}/{files_total}] Unknown project type {type_}. Considering as mod...")

                destination_dir = os.path.join(args.destination_dir, root_dir)

                # Try to find file to download (for check) and find if we have previous versions in destination dir
                file_size = 0
                file_to_download_name = None
                files_to_delete = []
                for file_ in project_info["files"]:
                    # Target version
                    if file_["id"] == file_id:
                        if not file_to_download_name:
                            file_to_download_name = file_["name"]
                            file_size = file_["filesize"]

                            # Exit from loop if we already have this file in destination dir and it's size is equal
                            dest_file = os.path.join(destination_dir, file_to_download_name)
                            if os.path.exists(dest_file) and os.path.getsize(dest_file) == file_size:
                                break

                    # Other versions
                    else:
                        file_to_delete = os.path.join(destination_dir, file_["name"])
                        if os.path.exists(file_to_delete):
                            files_to_delete.append(file_to_delete)

                # Check if target file exists in available files (just in case)
                if not file_to_download_name:
                    logging.warning(f"[{i + 1}/{files_total}] No file {file_id}. Skipping project {project_id}")
                    continue

                destination = os.path.join(destination_dir, file_to_download_name)

                # Skip if we already have this file in destination dir
                if os.path.exists(destination):
                    logging.info(f"[{i + 1}/{files_total}] File {file_to_download_name} already exists")
                    continue

                # Make dirs if not exists
                if not os.path.exists(destination_dir):
                    logging.info(f"[{i + 1}/{files_total}] Creating directory {destination_dir}")
                    os.makedirs(destination_dir)

                # Build URL and download
                download_url = DOWNLOAD_URL.format(project_id=project_id, file_id=file_id)

                attempts = 0
                while True:
                    try:
                        attempts += 1
                        logging.info(f"[{i + 1}/{files_total}] Downloading {download_url} as {file_to_download_name}")
                        with request.urlopen(download_url) as response, open(destination, "w+b") as out_file:
                            shutil.copyfileobj(response, out_file)
                            out_file.flush()
                            os.fsync(out_file.fileno())
                        if not os.path.exists(destination) or os.path.getsize(destination) != file_size:
                            raise Exception("File doesn't exists or has a wrong size")
                        break
                    except Exception as e:
                        logging.error(f"Unable to download {download_url}", exc_info=e)

                    if attempts >= FILE_DOWNLOAD_MAX_ATTEMPTS:
                        raise Exception(f"Unable to download file in {FILE_DOWNLOAD_MAX_ATTEMPTS} attempts")

                    time.sleep(1)
                    logging.warning("Retrying...")

                # Delete previous versions
                for file_to_delete in files_to_delete:
                    logging.warning(
                        f"[{i + 1}/{files_total}] Deleting previous version {os.path.basename(file_to_delete)}"
                    )
                    os.remove(file_to_delete)

            #######################
            # Deal with overrides #
            #######################
            overrides = manifest.get("overrides")
            if overrides:
                overrides_dir = os.path.join(temp_dir, overrides)

                override_file_paths = []
                for root, _, f_names in os.walk(overrides_dir):
                    for override_file_path in f_names:
                        override_file_paths.append(os.path.join(root, override_file_path))

                getch_ = Getch()
                for override_file in override_file_paths:
                    override_file_rel = os.path.relpath(override_file, overrides_dir)
                    override_file_target = os.path.join(args.destination_dir, override_file_rel)

                    # Copy if not exists
                    if not os.path.exists(override_file_target):
                        file_copy(override_file, override_file_target, rewrite=True)
                        continue

                    # Calculate checksums for comparing them
                    checksum_src = file_md5(override_file)
                    checksum_target = file_md5(override_file_target)

                    # Skip file if match
                    if checksum_src == checksum_target:
                        logging.info(f"Skipping file {override_file_rel}. Already exists")
                        continue

                    # CLI action provided
                    if args.skip:
                        logging.info(f"Skipping file {override_file_rel}")
                        continue
                    elif args.rename:
                        file_copy(override_file, override_file_target, rewrite=False)
                        continue
                    elif args.overwrite:
                        file_copy(override_file, override_file_target, rewrite=True)
                        continue

                    # Find differences
                    diffs = []
                    with open(override_file_target, "r", encoding="utf-8", errors="replace") as file_old, open(
                        override_file, "r", encoding="utf-8", errors="replace"
                    ) as file_new:
                        for line in unified_diff(file_old.readlines(), file_new.readlines(), lineterm=""):
                            diffs.append(line.strip())

                    # No text diffs found (strange? Not really. Maybe it's just extra new lines) -> rename to .old
                    if len(diffs) == 0:
                        logging.warning(
                            f"Checksums of files {override_file_rel} don't match but no text difference found! Creating backup and overwriting"
                        )
                        file_copy(override_file, override_file_target, rewrite=False)
                        logging.warning("Please consider checking these files manually and removing unnecessary ones")
                        continue

                    # Print difference and ask user
                    logging.warning(
                        f"Your {override_file_rel} is different from the downloaded one. Please select what to do"
                    )
                    print("\nDifference:")
                    print("\n".join(diffs).strip(), end="\n\n")
                    print(
                        "[s]kip - keep your version | [o]verwrite - replace with downloaded | [r]ename old file by adding .old | [e]xit - cancel and exit (press s, o, r or e):",
                        end=" ",
                        flush=True,
                    )
                    while True:
                        pressed_key = getch_()
                        print(str(pressed_key), flush=True)
                        if pressed_key and (
                            str(pressed_key).lower() == "s"
                            or str(pressed_key).lower() == "o"
                            or str(pressed_key).lower() == "r"
                            or str(pressed_key).lower() == "e"
                        ):
                            break
                        print(
                            "Please select what to do: [s]kip, [o]verwrite, [r]ename or [e]xit:",
                            end=" ",
                            flush=True,
                        )

                    # Abort requested
                    if str(pressed_key).lower() == "e":
                        raise KeyboardInterrupt()

                    # Keep user version
                    if str(pressed_key).lower() == "s":
                        logging.info(f"Skipping file {override_file_rel}")
                        continue

                    # Rename
                    if str(pressed_key).lower() == "r":
                        file_copy(override_file, override_file_target, rewrite=False)
                        continue

            ##################
            # Download forge #
            ##################
            if (
                "minecraft" in manifest
                and "version" in manifest["minecraft"]
                and "modLoaders" in manifest["minecraft"]
                and len(manifest["minecraft"]["modLoaders"]) != 0
            ):
                mod_loader_id = manifest["minecraft"]["modLoaders"][0]["id"]

                # Forge
                if mod_loader_id.startswith("forge-"):
                    download_url = FORGE_URL.format(
                        game_version=manifest["minecraft"]["version"], forge_version=mod_loader_id[6:]
                    )
                    destination = download_url.split("/")[-1].strip()
                    if not destination:
                        destination = download_url.split("/")[-2].strip()
                    destination = os.path.join(args.destination_dir, destination)
                    logging.info(f"Downloading {download_url} as {destination}")
                    request_ = request.Request(download_url, headers={"User-Agent": args.user_agent})
                    with request.urlopen(request_) as response, open(destination, "w+b") as out_file:
                        shutil.copyfileobj(response, out_file)
                    logging.info(
                        f'Forge {mod_loader_id[6:]} downloaded. Please run java -jar "{destination}"'
                        " to install client and use --installServer argument to install server"
                    )

                # Fabric
                if mod_loader_id.startswith("fabric"):
                    destination = os.path.join(args.destination_dir, FABRIC_FILE_NAME)
                    logging.info(f"Downloading {FABRIC_URL} as {destination}")
                    request_ = request.Request(FABRIC_URL, headers={"User-Agent": args.user_agent})
                    with request.urlopen(request_) as response, open(destination, "w+b") as out_file:
                        shutil.copyfileobj(response, out_file)
                    logging.info(
                        f"Fabric installer downloaded."
                        f' Please run java -jar "{destination}" client -dir {args.destination_dir} -mcversion'
                        f' "target minecraft version" -loader "target fabric version" to install client'
                    )

                # Unknown mod loader (yet)
                else:
                    logging.warning(f"Please download {mod_loader_id} mod loader manually")

            # Done
            logging.info(f"{manifest['name']} v{manifest['version']} downloaded")
            logging.info("curseforge-modpack-downloader finished")

        # Handle CTRL+C
        except (SystemExit, KeyboardInterrupt):
            logging.warning("Canceled")

        # Handle errors (for now, just log them)
        except Exception as e:
            logging.error(e)


if __name__ == "__main__":
    main()
