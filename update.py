import datetime
import os
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

build_repo_name = "kraxarn/spotify-qt-builds"
source_repo_name = "kraxarn/spotify-qt"


def get_latest_artifact_url(workflow_id: int) -> str:
	artifacts_url = requests \
		.get(f"https://api.github.com/repos/{source_repo_name}/actions/workflows/{workflow_id}/runs", headers=headers) \
		.json()["workflow_runs"][0]["artifacts_url"]

	return requests.get(artifacts_url, headers=headers) \
		.json()["artifacts"][0]["archive_download_url"]


def download_file(source: str, target: str):
	with requests.get(source, headers=headers, stream=True) as response:
		with open(target, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)
				downloaded += len(chunk)
				percent = int((downloaded / total_size) * 100)
				if percent != last_percent and percent % 10 == 0:
					print(f".", end="")
					last_percent = percent


for workflow in workflows:
	url = get_latest_artifact_url(workflow)
	filename = workflows[workflow]
	print(f"Downloading {filename}", end="")
	download_file(url, size, filename)
	print("")

# print(f"Builds updated: {build_repo.updated_at}")
# print(f"Source updated: {source_repo.updated_at}")

# if build_repo.updated_at > source_repo.updated_at:
# 	print("Already up-to-date")
# 	sys.exit()

# build_updated_days = (datetime.datetime.now() - build_repo.updated_at).days
# build_updated_days_suffix = "day" if build_updated_days == 1 else "days"
# print(f"Builds were updated {build_updated_days} {build_updated_days_suffix} ago")
