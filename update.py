import datetime
import json
import os
import sys
import typing
import zipfile

import requests

# Access token needs to be set for GitHub API calls
if "ACCESS_TOKEN" not in os.environ:
	sys.exit("Error: Access token not specified")

access_token = os.environ["ACCESS_TOKEN"]

headers = {
	"Accept": "application/vnd.github.v3+json",
	"Authorization": f"token {access_token}",
}

build_repo_name: typing.Final[str] = "kraxarn/spotify-qt-nightly"
source_repo_name: typing.Final[str] = "kraxarn/spotify-qt"


def get_latest_artifact_url(workflow_id: int) -> str:
	runs_url = f"https://api.github.com/repos/{source_repo_name}/actions/workflows/{workflow_id}/runs"
	runs = requests.get(runs_url, headers=headers).json()["workflow_runs"]
	latest_run = runs[0]

	if latest_run["event"] == "push" and latest_run["conclusion"] == "success":
		artifacts_url = latest_run["artifacts_url"]
	else:
		raise ValueError("Latest run failed")

	artifacts = requests.get(artifacts_url, headers=headers).json()
	return artifacts["artifacts"][0]["archive_download_url"]


def download_file(source: str, target: str):
	with requests.get(source, headers=headers, stream=True) as response:
		with open(target, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)


def download_artifact(workflow_id: int, destination: str):
	if "--no-download" in sys.argv and os.path.isfile(destination):
		return
	artifact_url = get_latest_artifact_url(workflow_id)
	download_file(artifact_url, destination)


def extract(file: str) -> str:
	extracted_file: str
	with zipfile.ZipFile(file, "r") as zip_file:
		extracted_file = zip_file.namelist()[0]
		zip_file.extractall()
	return extracted_file


def get_latest_source_hash() -> str:
	commits_url = f"https://api.github.com/repos/{source_repo_name}/commits"
	return requests.get(commits_url, headers=headers).json()[0]["sha"]


def get_latest_build_release() -> typing.Any:
	latest_release_url = f"https://api.github.com/repos/{build_repo_name}/releases/latest"
	return requests.get(latest_release_url, headers=headers).json()


def get_latest_build_hash() -> str:
	release = get_latest_build_release()
	return str(release["body"]).partition("\n")[0].rstrip()


def get_latest_build_release_id() -> int:
	return get_latest_build_release()["id"]


def get_latest_source_tag() -> str:
	tags_url = f"https://api.github.com/repos/{source_repo_name}/tags"
	return requests.get(tags_url, headers=headers).json()[0]["name"]


def get_target_version() -> str:
	today = datetime.datetime.today()
	return today.strftime("%y%m%d")


def get_changes(sha: str) -> typing.Generator[str, str, None]:
	commits_url = f"https://api.github.com/repos/{source_repo_name}/commits"
	commits = requests.get(commits_url, headers=headers).json()
	for commit in commits:
		if str(commit["sha"]).startswith(sha):
			break
		message = commit["commit"]["message"]
		yield f"* {message}"


def update_release(release_id: int, commit_hash: str, changes: typing.Iterable[str]):
	today = datetime.date.today()
	data = json.dumps({
		"name": today.strftime("%b %d, %Y"),
		"body": "\n".join([
			commit_hash,
			*changes,
		])
	})
	release_url = f"https://api.github.com/repos/{build_repo_name}/releases/{release_id}"
	requests.patch(release_url, data=data, headers=headers)


def add_release_asset(release_id: int, filename: str):
	assets_url = (
		f"https://uploads.github.com/repos/{build_repo_name}/releases/{release_id}/assets"
		f"?name={filename}"
	)
	upload_headers = headers
	upload_headers["Content-Type"] = "application/octet-stream"
	with open(filename, "rb") as file:
		requests.post(assets_url, headers=upload_headers, data=file)


def delete_release_asset(asset_id: int):
	asset_url = f"https://api.github.com/repos/{build_repo_name}/releases/assets/{asset_id}"
	requests.delete(asset_url, headers=headers)


def get_all_assets() -> typing.Generator[int, int, None]:
	for asset in get_latest_build_release()["assets"]:
		yield asset["id"]


def download_artifact_and_extract(workflow_id: int, filename: str):
	download_target = f"{workflow_id}.zip"
	download_artifact(workflow_id, download_target)
	os.rename(extract(download_target), filename)


def find_workflow_id(name: str) -> int:
	workflows_url = f"https://api.github.com/repos/{source_repo_name}/actions/workflows"
	workflows = requests.get(workflows_url, headers=headers).json()["workflows"]
	for workflow in workflows:
		if workflow["name"] == name:
			return workflow["id"]
	raise ValueError(f"Workflow not found: {name}")


source_tag = get_latest_source_tag()
source_hash = get_latest_source_hash()
source_version = f"{source_tag}-{source_hash[0:7]}"
target_version = f"{source_tag}-{get_target_version()}"

build_hash = get_latest_build_hash()

if source_hash == build_hash and "--force" not in sys.argv:
	print(f"Builds are up-to-date ({source_hash})")
	exit()

print(f"Updating builds to {source_version}")

# Linux
print("Downloading Linux build")
file_linux = f"spotify-qt-{target_version}.AppImage"
workflow_id_linux = find_workflow_id("Linux")
download_artifact_and_extract(workflow_id_linux, file_linux)
print(f"Linux build saved to: {file_linux}")

# macOS
print("Downloading macOS build")
file_macos = f"spotify-qt-{target_version}.dmg"
workflow_id_macos = find_workflow_id("macOS")
download_artifact_and_extract(workflow_id_macos, file_macos)
print(f"macOS build saved to: {file_macos}")

# Windows x64
print("Downloading Windows build")
file_win64 = f"spotify-qt-{target_version}-win64.zip"
workflow_id_win64 = find_workflow_id("Windows")
download_artifact(workflow_id_win64, file_win64)
print(f"Windows x64 build saved to: {file_win64}")

# Update release
print("Updating release")
latest_release_id = get_latest_build_release_id()
update_release(latest_release_id, source_hash, get_changes(build_hash))

# Delete all old assets
for release_asset_id in get_all_assets():
	delete_release_asset(release_asset_id)

# Update builds
print("Uploading Linux build")
add_release_asset(latest_release_id, file_linux)
print("Uploading macOS build")
add_release_asset(latest_release_id, file_macos)
print("Uploading Windows build")
add_release_asset(latest_release_id, file_win64)
