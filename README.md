# DOJ CRT Portal

A civil rights complaint portal built using the Acquia [BLT](https://github.com/acquia/blt) Drupal stack.

# Getting Started

This project is based on BLT, a  template and tool that enables building, testing, and deploying Drupal from Acquia.

1. Request access to the Acquia Cloud Environment for your project (if needed).

2. Setup a SSH key that can be used for GitHub and the Acquia Cloud (you CAN use the same key).
    1. [Setup GitHub SSH Keys](https://help.github.com/articles/adding-a-new-ssh-key-to-your-github-account/)
    2. [Setup Acquia Cloud SSH Keys](https://docs.acquia.com/acquia-cloud/ssh/generate)

3. Clone this repository. By default, Git names this "origin" on your local machine.

```
git clone git@github.com:usdoj/crt-portal.git
```

4. Update your the configuration located in the `/blt/blt.yml` file to match your site's needs. See [configuration files](#important-configuration-files) for other important configuration files.

# Setup Local Environment

## Core Setup

#### 1. Install VM dependencies

Running your local environment requires VirtualBox and Vagrant. Install both locally:

- https://www.virtualbox.org/
- https://www.vagrantup.com/downloads.html

#### 2. Install Composer dependencies locally

From the root directory of this project:

```
composer install
```

#### 3. Setup a local blt alias

You should be able to run `blt` from the root of your project and see a list of `blt` commands.

If blt is not available at the root of your project, use this command to set up a blt alias (one time only):

```
composer run-script blt-alias
```

#### 4. Install DrupalVM setup using blt vm

```
blt vm
```

#### 5. Setup VM

Setup the VM with the configuration from this repositories [configuration files](#important-configuration-files).

```
vagrant up
```

If this throws errors, you may need to manually `vagrant ssh` into the box and install missing dependencies to satisfy error messages.

#### 6. Check vagrant status

See the status of your virtual machines:

```
vagrant global-status
```

You should see a row with "name" equal to "dojportal-blt" and "state" equal to "running."

## ... I want to visit my site locally

http://local.dojportal-blt.com/

If you don't see anything, check your `/etc/hosts` file or adjust the port forwarding settings in your `Vagrantfile`.

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

---
## Other Local Setup Steps

1. Set up frontend build and theme.
By default BLT sets up a site with the lightning profile and a cog base theme. You can choose your own profile before setup in the blt.yml file. If you do choose to use cog, see [Cog's documentation](https://github.com/acquia-pso/cog/blob/8.x-1.x/STARTERKIT/README.md#create-cog-sub-theme) for installation.
See [BLT's Frontend docs](https://docs.acquia.com/blt/developer/frontend/) to see how to automate the theme requirements and frontend tests.
After the initial theme setup you can configure `blt/blt.yml` to install and configure your frontend dependencies with `blt setup`.

2. Pull Files locally.
Use BLT to pull all files down from your Cloud environment.

   ```
   $ blt drupal:sync:files
   ```

3. Sync the Cloud Database.
If you have an existing database you can use BLT to pull down the database from your Cloud environment.
   ```
   $ blt sync
   ```


---

# Resources

Additional [BLT documentation](https://docs.acquia.com/blt/) may be useful. You may also access a list of BLT commands by running this:
```
$ blt
```

Note the following properties of this project:
* Primary development branch: #GIT_PRIMARY_DEV_BRANCH
* Local environment: #LOCAL_DEV_SITE_ALIAS
* Local site URL: #LOCAL_DEV_URL

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
