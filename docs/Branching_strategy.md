## Branching strategy:

This strategy is aimed at reducing the risk of production deploys. Smaller, more frequent deploys reduce the risk of each deploy. Since these smaller deploys are less likely to cause problems, that provides the benefit of less downtime and higher availability of your systems. It also has the benefit of better schedules for maintainers since there is rarely a need to wait until the site is not in use if you can do seamless deploys.

So, the overall goal is to make sure that we have small, frequent deploys while ensuring proper quality checks. Before code is deployed it goes though 3 human evaluations and at least 3 rounds of automated testing.

We currently have automated tests for:
        - accessibility
        - security
        - business logic

Automated testing doesn't replace the need for people with context who are approving work, but it does reduce the risk of introducing errors or vulnerabilities. It can make sure certain bugs are not reintroduced and catch common security and accessibility errors.

----

### Step one, PR review:

Someone creates code or app changes as described in a ticket. After that standalone task or story from a ticket is completed, that portion of code is proposed as a pull request. This first check see [PR documentation](https://github.com/usdoj-crt/crt-portal/blob/master/docs/pull_requests.md) for complete checks.

It ensures:
- Human quality check for:
    - fulfilling the need described in the ticket
    - security
    - code quality (making sure it is understandable so that future O&M is easier)
- Automated tests
    - important business logic requirements should be captured in tests
    - key functionality should be checked with tests

Once code is merged into the develop branch, the code is deployed to the development instance and the card describing the work goes into the "dev done" column. This step can happen at anytime.


### Step two, Release QA:

Releases are created every two weeks as part of the a two week sprint cadence. Product owners and managers approve the work in the develop branch to become a release. This is represented in two processes on the project scrum board; the initial check that the product owner moves cards from "dev done" to "ready for UAT".

The work from the develop branch is made into a new branch named `release/date-of-planed-release`

There will then be a couple days for QA. Generally we will want to check it matches Acceptance Criteria, if there are unusual bugs or inconsistencies and it should be ready to bring in the relevant business interests to approve.

Automated tests are run on any code corrections via a PR and PR review to the release branch.


### Step three:

 Once customer sign off is done, the product owner or their designee gives final approval of the staging site and the deploy to the production environment.

 The release is merged into the development branch to make sure any of the adjustments in staging are also accounted for upstream.

 The release branch, `release/date-of-planed-release` is merged into the `master` branch, which triggers the final run of the automated testing suite. If this is successful, the code is deployed automatically.

 A successful deploy is communicated to the team, and there is a quick check to make sure the release went smoothly.

----

## Timeline

Week |Monday |Tuesday |Wednesday |Thursday |Friday
--|--|--|--|--|--
Week 1 | |Sprint begins |Create a `release/...` branch to deploy to staging | |
Week 2 |Merge the `release/...` branch into `master` to deploy to production | Next Sprint begins| | |


The main workflow is based on a [GitFlow](https://danielkummer.github.io/git-flow-cheatsheet/) approach, but you don't need to know or use GitFlow for this to work.

----

### Contingency
**Hotfixes** are the way that we approach critical bugs or flaws found in production. When this happens, a business owner or their designee will request a hotfix. Once the solution is identified, the hotfix will undergo PR review and QA at the same time. The branch is then merged into the develop branch. Once automated tests pass, there is a quick QA, then the code is merged into the upcoming release. This auto-deploys after tests with a short QA period. Then the code will be merged into master, which will also auto-deploy after tests.
