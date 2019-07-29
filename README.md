# DOJ CRT Portal

A Civil Rights complaints portal built using the Acquia [BLT](https://github.com/acquia/blt) Drupal stack. BLT is a template and tool for building, testing, and deploying Drupal from Acquia.

# Acquia Cloud and git setup

1. Request access to the Acquia Cloud Environment for your project (if needed).

2. Setup a SSH key that can be used for GitHub and the Acquia Cloud (you CAN use the same key).
    1. [Setup GitHub SSH Keys](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/)
    2. [Setup Acquia Cloud SSH Keys](https://docs.acquia.com/acquia-cloud/ssh/generate)

3. Clone this repository. By default, Git names this "origin" on your local machine.

```
git clone git@github.com:usdoj/crt-portal.git
```

# Local Environment Setup

#### 1. Install VM dependencies

Running your local environment requires VirtualBox and Vagrant. Install both locally:

- https://www.virtualbox.org/
- https://www.vagrantup.com/downloads.html

If the VirtualBox installation process ends with an error screen on MacOS, you may need to follow [these obscure steps](https://ilgthegeek.wordpress.com/2018/01/27/macos-install-oracle-virtualbox-on-10-13/) and try re-installing.

#### 2. Install php and Composer

Install php if you don't already have it on your machine:

- https://php.net/

Download Composer:

- https://getcomposer.org/download/

You may have to take additional steps to make composer available anywhere in your Terminal, such as:

```
mv composer.phar /usr/local/bin/composer
```

See https://getcomposer.org/doc/00-intro.md for more information.

You should be able to run composer from the root directory of this project and see a list of composer commands.

#### 3. Install Composer dependencies locally

From the root directory of this project:

```
composer install
```

#### 4. Setup a local blt alias

Add the following to your `~/.bash_profile` or equivalent to create a local alias to the `blt` tool:

```
function blt() {
  if [[ ! -z ${AH_SITE_ENVIRONMENT} ]]; then
    PROJECT_ROOT="/var/www/html/${AH_SITE_GROUP}.${AH_SITE_ENVIRONMENT}"
  elif [ "`git rev-parse --show-cdup 2> /dev/null`" != "" ]; then
    PROJECT_ROOT=$(git rev-parse --show-cdup)
  else
    PROJECT_ROOT="."
  fi

  if [ -f "$PROJECT_ROOT/vendor/bin/blt" ]; then
    $PROJECT_ROOT/vendor/bin/blt "$@"

  # Check for local BLT.
  elif [ -f "./vendor/bin/blt" ]; then
    ./vendor/bin/blt "$@"

  else
    echo "You must run this command from within a BLT-generated project."
    return 1
  fi
}

```

#### 5. Install DrupalVM setup using blt vm

```
blt vm
```

#### 6. Setup VM

Setup the VM with the configuration from this repositories [configuration files](#important-configuration-files).

```
vagrant up
```

This task may fail with the following error:

```
pip: command not found
```

You will need to fix this by logging into the box and installing pip and ansible manually:

```
vagrant ssh
sudo apt install python-pip
pip install --upgrade ansible
```

If `vagrant up` did not run successfully, you may need to run:

```
vagrant reload --provision
```

#### 7. Check vagrant status

See the status of your virtual machines:

```
vagrant global-status
```

You should see a row with "name" equal to "dojportal-blt" and "state" equal to "running."

## ... I want to visit my site locally

http://local.dojportal-blt.com/

If you don't see anything, check your `/etc/hosts` file or adjust the port forwarding settings in your `Vagrantfile`.

## ... I want to run drush commands against Acquia Cloud sites

Follow the "Acquia Cloud aliases" instructions on https://docs.acquia.com/blt/developer/drush/:

> You can download aliases for Acquia Cloud sites by signing in to https://cloud.acquia.com, and then going to the Credentials tab on your user profile. Download and place the relevant alias file into drush/sites.

Cheeck to see if your drush aliases are set up correctly:

```
drush sa
```

### Troubleshooting Drush/BLT commands

When you run into set up errors, using the `--verbose` flag can give valuable info for debugging

## ... I want to set up a new Drupal site

After you've completed steps 1 through 6 above:

#### 1. SSH into your VM

```
vagrant ssh
```

#### 2. Set up blt alias within the VM

```
composer run-script blt-alias
```

#### 3. Setup a local Drupal site with an empty database.
Use BLT to setup the site with configuration.  If it is a multisite you can identify a specific site.

```
blt setup
```
or

```
blt setup --site=[sitename]
```

#### 4. Log into your site with drush

Log into the VM and run the following commands within your VM:

```
cd docroot
drush uli
```

## ... I want to import configuration locally

First, download the configuration you want to import to `config/default`. (Or switch to a branch which contains the configuration you need in `config/default`.)

Make sure your drush config is set to match the UUID of the Drupal site you would like to import from. In the case of our app, use:

```
# from within vagrant ssh

drush config-set "system.site" uuid "3bb8cee4-7729-4ef8-acb0-46ca31a0d55d"
```

Once the UUID matches, you should be able to run:

```
# from within vagrant ssh

drush cim
```

## ... I want to customize the project theme

This project uses the [Drupal USWDS base theme](https://www.drupal.org/project/uswds). Its active theme is a subtheme called `crt_portal_subtheme`.

To customize the subtheme using Sass, edit the `_variables.scss` and `uswds.scss` override files in the `crt_portal_subtheme` folder, and then regenerate the CSS:

```
cd docroot/themes/custom/crt_portal_subtheme/
npm install
cp -r node_modules/uswds/dist assets
npm run build
```

Or use "watch" mode to regenerate the CSS whenever the Sass is edited:

```
...
npm run build:watch
```

## Other BLT Steps

#### Pull Files locally.
Use BLT to pull all files down from your Cloud environment.

```
blt drupal:sync:files
```

#### Sync the Cloud Database.
If you have an existing database you can use BLT to pull down the database from your Cloud environment.

```
blt sync
```

# Deploy

First, make sure you have the `ACQUIA_CLOUD_REMOTE_GIT` variable set in your `set_environment_variables` script. This represents the git location for the project you want to deploy to, and is available in Acquia Cloud.

```
cp example.set_environment_variables.sh set_environment_variables.sh

{set value for ACQUIA_CLOUD_REMOTE_GIT}

chmod +x set_environment_variables.sh

source set_environment_variables.sh
```

Next:

```
blt artifact:deploy --commit-msg "BLT-001: Commit message here." --branch "branch name here" --no-interaction
```

Note that by default, commit messages need to conform to a strict pattern specified in `build.yml` under `git > commit-msg > pattern`. The default regex pattern is as follows, with "project.prefix" being "BLT" by default:

`"/(^${project.prefix}-[0-9]+(: )[^ ].{15,}\\.)|(Merge branch (.)+)/"`

Also note that this regex requires a period at the end of the commit message.

## Installing, deploying, and enabling a new module

1. Install and enable the module locally
2. Export configuration locally (eg, `drush @dojportal-blt.local cex`)
3. Commit the exported configuration
4. Deploy to Acquia (see deploy commands above)
5. Import the configuration to Acquia (eg, `drush @dojportal-blt.dev cim`)
6. When you have a choice to use "sync" or "vcs", choose "vcs".

# Resources

Additional [BLT documentation](https://docs.acquia.com/blt/) may be useful. You may also access a list of BLT commands by running this:

```
blt
```

<!---
Note the following properties of this project:
* Primary development branch: #GIT_PRIMARY_DEV_BRANCH
* Local environment: #LOCAL_DEV_SITE_ALIAS
* Local site URL: #LOCAL_DEV_URL
--->

## Working With a BLT Project

BLT projects are designed to instill software development best practices (including git workflows).

Our BLT Developer documentation includes an [example workflow](https://docs.acquia.com/blt/developer/dev-workflow/).

### Important Configuration Files

BLT uses a number of configuration (`.yml` or `.json`) files to define and customize behaviors. Some examples of these are:

* `blt/blt.yml` (formerly blt/project.yml prior to BLT 9.x)
* `blt/local.blt.yml` (local only specific blt configuration)
* `box/config.yml` (if using Drupal VM)
* `drush/sites` (contains Drush aliases for this project)
* `composer.json` (includes required components, including Drupal Modules, for this project)
