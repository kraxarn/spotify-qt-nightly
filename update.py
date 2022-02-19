import datetime
import os
import subprocess
import sys

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


def run(args: list[str]):
	subprocess.run(args)


def add_file(name: str):
	run(["git", "add", name])


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

print(f"Updating builds to {latest_source}...")

# for workflow in workflows:
# 	url = get_latest_artifact_url(workflow)
# 	filename = workflows[workflow]
# 	print(f"Downloading {filename}...")
# 	download_file(url, filename)
# 	add_file(filename)
#
# run(["git", "commit", "-m", source_hash()])

# print(f"Builds updated: {build_repo.updated_at}")
# print(f"Source updated: {source_repo.updated_at}")

# if build_repo.updated_at > source_repo.updated_at:
# 	print("Already up-to-date")
# 	sys.exit()

# build_updated_days = (datetime.datetime.now() - build_repo.updated_at).days
# build_updated_days_suffix = "day" if build_updated_days == 1 else "days"
# print(f"Builds were updated {build_updated_days} {build_updated_days_suffix} ago")
