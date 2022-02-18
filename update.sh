export BUILD_REPO="kraxarn/spotify-qt-builds"
export SOURCE_REPO="kraxarn/spotify-qt"
export HEADER="Authorization: token $ACCESS_TOKEN"

#workflows=(
#	[7734249]="spotify-qt-linux-nightly.AppImage"
#	[18195390]="spotify-qt-win64-nightly.zip"
#	[18401182]="spotify-qt-win32-nightly.zip"
#	[18407206]="spotify-qt-macos-nightly.dmg"
#)

#workflow_ids=(7734249 18195390 18401182 18407206)
#workflow_sources=(
#	"spotify-qt-linux-nightly.zip"
#	"spotify-qt-win64-nightly.zip"
#	"spotify-qt-win32-nightly.zip"
#	"spotify-qt-macos-nightly.zip"
#)
#workflow_targets=(
#	"spotify-qt-linux-nightly.AppImage"
#	"spotify-qt-win64-nightly.zip"
#	"spotify-qt-win32-nightly.zip"
#	"spotify-qt-macos-nightly.dmg"
#)
#workflow_zipped=(true false false true)

latest_artifact_url() {
	runs_url="https://api.github.com/repos/$SOURCE_REPO/actions/workflows/$1/runs"
	artifacts_url=$(curl -s -H "$HEADER" "$runs_url" | jq -r '.workflow_runs[0].artifacts_url')
	curl -s -H "$HEADER" "$artifacts_url" | jq -r '.artifacts[0].archive_download_url'
}

download_file() {
	echo "Download: $1"
	curl -L -H "$HEADER" "$1" -o "$2"
}

url="$(latest_artifact_url "7734249")"

download_file "$url" "target.zip"