import os
import sys
import zipfile

import requests

# Access token needs to be set for GitHub API calls
if "ACCESS_TOKEN" not in os.environ:
	sys.exit("Error: Access token not specified")

workflows = {
	7734249: "spotify-qt-linux-nightly.AppImage",
	18195390: "spotify-qt-win64-nightly.zip",
	18401182: "spotify-qt-win32-nightly.zip",
	18407206: "spotify-qt-macos-nightly.dmg",
}

access_token = os.environ["ACCESS_TOKEN"]

headers = {
	"Authorization": f"token {access_token}",
}

build_repo_name = "kraxarn/spotify-qt-nightly"
source_repo_name = "kraxarn/spotify-qt"


def get_latest_artifact_url(workflow_id: int) -> str:
	runs_url = f"https://api.github.com/repos/{source_repo_name}/actions/workflows/{workflow_id}/runs"
	runs = requests.get(runs_url, headers=headers) \
		.json()["workflow_runs"]

	artifacts_url = ""
	for run in runs:
		if run["event"] == "push" and run["conclusion"] == "success":
			artifacts_url = run["artifacts_url"]
			break

	if len(artifacts_url) == 0:
		raise ValueError("No artifact found")

	return requests.get(artifacts_url, headers=headers) \
		.json()["artifacts"][0]["archive_download_url"]


def download_file(source: str, target: str):
	with requests.get(source, headers=headers, stream=True) as response:
		with open(target, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)


def download_artifact(workflow_id: int, destination: str):
	artifact_url = get_latest_artifact_url(workflow_id)
	download_file(artifact_url, destination)


def extract(file: str) -> str:
	extracted_file: str
	with zipfile.ZipFile(file, "r") as zip_file:
		extracted_file = zip_file.namelist()[0]
		zip_file.extractall()
	return extracted_file


def source_hash() -> str:
	return requests.get(f"https://api.github.com/repos/{source_repo_name}/commits", headers=headers) \
		.json()[0]["sha"]


def get_latest_tag(repo: str) -> str:
	return requests.get(f"https://api.github.com/repos/{repo}/tags", headers=headers) \
		.json()[0]["name"]


def get_latest_source_version() -> str:
	tag = get_latest_tag(source_repo_name)
	short_hash = source_hash()[0:7]
	return f"{tag}-{short_hash}"


def get_latest_build_version() -> str:
	return get_latest_tag(build_repo_name)


latest_source = get_latest_source_version()
latest_build = get_latest_build_version()

if latest_source == latest_build and "--force" not in sys.argv:
	print(f"Builds are up-to-date ({latest_build})")
	exit()

print(f"Updating builds to {latest_source}")

# Linux
print("Downloading Linux build")
download_artifact(7734249, "linux.zip")
print("Extracting file")
file_linux = extract("linux.zip")
print(f"Linux build saved to: {file_linux}")

# macOS
print("Downloading macOS build")
download_artifact(18407206, "macos.zip")
print("Extracting file")
file_macos = extract("macos.zip")
print(f"macOS build saved to: {file_macos}")
