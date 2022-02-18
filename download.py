import datetime
import os
import subprocess
import sys
import requests

# Access token needs to be set for GitHub API calls
if "ACCESS_TOKEN" not in os.environ:
	sys.exit("Error: Access token not specified")

if len(sys.argv) != 3:
	basename = os.path.basename(sys.argv[0])
	sys.exit(f"Usage: {basename} <workflow-id> <output-file>")

workflow_id = sys.argv[1]
output_file = sys.argv[2]

access_token = os.environ["ACCESS_TOKEN"]

headers = {
	"Authorization": f"token {access_token}",
}

build_repo_name = "kraxarn/spotify-qt-builds"
source_repo_name = "kraxarn/spotify-qt"


def get_latest_artifact_url() -> str:
	artifacts_url = requests \
		.get(f"https://api.github.com/repos/{source_repo_name}/actions/workflows/{workflow_id}/runs", headers=headers) \
		.json()["workflow_runs"][0]["artifacts_url"]

	return requests.get(artifacts_url, headers=headers) \
		.json()["artifacts"][0]["archive_download_url"]


def download_file(source: str):
	with requests.get(source, headers=headers, stream=True) as response:
		with open(output_file, "wb") as file:
			for chunk in response.iter_content(chunk_size=8192):
				file.write(chunk)


url = get_latest_artifact_url()
download_file(url)
