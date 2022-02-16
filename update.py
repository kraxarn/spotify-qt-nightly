import datetime
import os
import sys
from github import WorkflowRun, Github

# Access token needs to be set for GitHub API calls
if "ACCESS_TOKEN" not in os.environ:
	sys.exit("Error: Access token not specified")

workflow_ids = {
	7734249,   # Linux
	18195390,  # Windows (Qt 6, x64)
	18401182,  # Windows (Qt 5, x86)
	18407206,  # macOS
}

api = Github(os.environ["ACCESS_TOKEN"])

build_repo = api.get_repo(458937795)
source_repo = api.get_repo(239120579)

for workflow_id in workflow_ids:
	workflow = source_repo.get_workflow(workflow_id)
	runs = workflow.get_runs()
	latest_run = source_repo.get_workflow_run(runs[0].id)
	print(f"Last {workflow.name} run: {latest_run.updated_at}")

# print(f"Builds updated: {build_repo.updated_at}")
# print(f"Source updated: {source_repo.updated_at}")

if build_repo.updated_at > source_repo.updated_at:
	print("Already up-to-date")
	sys.exit()

# build_updated_days = (datetime.datetime.now() - build_repo.updated_at).days
# build_updated_days_suffix = "day" if build_updated_days == 1 else "days"
# print(f"Builds were updated {build_updated_days} {build_updated_days_suffix} ago")
