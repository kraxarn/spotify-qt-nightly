export SOURCE_REPO="kraxarn/spotify-qt"
export HEADER="Authorization: token $ACCESS_TOKEN"

latest_artifact_url() {
	runs_url="https://api.github.com/repos/$SOURCE_REPO/actions/workflows/$1/runs"
	echo "Found runs url: $runs_url"
	artifacts_url=$(curl -s -H "$HEADER" "$runs_url" | jq -r '.workflow_runs[0].artifacts_url')
	echo "Found artifacts url: $artifacts_url"
	curl -s -H "$HEADER" "$artifacts_url" | jq -r '.artifacts[0].archive_download_url'
}

download_file() {
	echo "Downloading: $1"
	curl -L -H "$HEADER" "$1" -o "$2"
}

download_artifact() {
	artifact_url="$(latest_artifact_url "$1")"
	download_file "$artifact_url" "$2"
}

source_hash() {
	commits_url="https://api.github.com/repos/$SOURCE_REPO/commits"
	curl -s -H "$HEADER" "$commits_url" | jq -r '.[0].sha'
}
