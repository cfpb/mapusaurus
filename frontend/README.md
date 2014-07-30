# Web Front End Framework for Mapusaurus

This exists outside of the Django project and writes to the cfpbstyle app.

We use the "CFPB Capital Framework" as our HTML framework, please see:

http://cfpb.github.io/capital-framework/cf-demo/#using-the-build-system

Ignored from Git:

# Django Templates: HTML, CSS, JS and Images

### 1. NodeJS & NPM

Assuming you are running Ubuntu 12.04, the default nodejs version is 0.6.12. Grunt requires Node 0.8 or later, so node needs to be installed this way:

```
sudo apt-get update
sudo apt-get install -y python-software-properties
sudo add-apt-repository ppa:chris-lea/node.js
sudo apt-get update
sudo apt-get install nodejs
```

Note: "sudo apt-get install nodejs" installs both node and npm now.

Note: Node Package Manager (npm) is the installer for Node.JS packages.

More info: http://stackoverflow.com/questions/12913141/installing-from-npm-fails

Verify the versions:

```
npm --version
node --version
```


### 3. Node Packages

These commands will install all the node packages that are listed in package.json. These are installed globally for the currently running use (vagrant).

```
cd /vagrant/mapusaurus/frontend
npm install
```


### 4. Bower Packages (Download JavaScript libraries)

Note: Up to this point we have been executing all the git commands in the mac terminal. Since the bower install command executes git clone commands, we need to configure git in the vagrant VM. Please see: https://help.github.com/articles/generating-ssh-keys

```
sudo npm install -g bower
bower install
```

Note: Some CFPB projects use "grunt vendor" to install the bower packages, which just downloads the "main" JS file. We are not using this method.


### 4. Grunt

Install grunt:

```
sudo npm install -g grunt-cli
```

Run grunt to build the "dist" or distrobution copy of the CSS and JS file

```
cd /vagrant/mapusaurus/frontend
grunt build
```
