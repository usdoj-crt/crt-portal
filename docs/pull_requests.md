# Pull Requests

## For creating a PR
Push your local branch to the repo
- While you are working on the branch you can add [WIP] for work in progress to the beginning of the title.
- Name your branch something descriptive
- Link to the ticket and copy the ticket contents over in the description of the PR
- Add screenshots of visual changes when appropriate.

Once you feel like you are ready for review
- Add any instructions or dependencies if needed to run the change
- Remove [WIP] from the title
- Assign a reviewer in GitHub

## For PR review
Once you are assigned as a reviewer
- Look over the files and make sure the code makes sense to you
- Make sure the code has documentation you that will be helpful for people maintaining the app in the future who may have less context
- Make sure any changes in how the app runs are reflected in the README.md file
- Look for anything that might make the app harder to maintain, if there is a chance to simplify the code make a note of it to discuss with the author
- Run the code locally
- If it is is for deployment, deploy the code
- If it is for logic, test the logic locally (and make sure there is an appropriate test)
- If it is a front end task, make sure renders as expected
- Make sure tests pass
- Think critically about any security concerns the PR may introduce. (Have those discussions off of GitHub.)
- We are not looking for perfection, we are looking for a solid base to iterate on. Things need to be secure and usable, but we can always make things better later.

Once the reviewer is satisfied with the PR:
- Merge the PR
- Delete the branch
