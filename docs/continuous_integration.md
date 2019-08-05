# Continuous Integration

## Server

The virtual server for the continuous integration can be reached using the following information.

- **IP**: 172.16.28.93
- **Hostname**: vm028093
- **Alias**: sprincl-ci.fe.hhi.de

The server can only be accessed via the Fraunhofer HHI internal LDAP user name and password. For access to the server, the IT helpdesk of the Fraunhofer HHI has to be contacted.

## Server Setup

The virtual server is running Ubuntu 18.04 LTS. The server was only setup with a basic firewall as follows.

```sh
# Allow connections for SSH and HTTP(s)
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Allow connections for systemd-resolved and systemd-network
sudo ufw allow 53/udp
sudo ufw allow 53/tcp
sudo ufw allow 68/udp

# Enables the firewall
sudo ufw enable
```

The the GitLab Runner was installed and configured as follows.

```sh
# Install the repository for the GitLab Runner (automatically performs sudo apt update)
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh | sudo bash

# Install the GitLab Runner, this automatically sets up most of the stuff needed by the runner
sudo apt install gitlab-runner

# Registers the GitLab Runner with the GitLab instance
sudo gitlab-runner register
sudo gitlab-runner start
```

The `gitlab-runner register command is an interactive tool, which expects all necessary information from standard input. The values that were chosen are in the following table The coordinator URL and the GitLab CI token for the runner can be found at [https://vigitlab.fe.hhi.de/bugspray/sprincl/-/settings/ci_cd](https://vigitlab.fe.hhi.de/bugspray/sprincl/-/settings/ci_cd) and may not be the same when setting up another runner.

| Setting         | Value                                                      |
|-----------------|------------------------------------------------------------|
| Coordinator URL | [https://vigitlab.fe.hhi.de/](https://vigitlab.fe.hhi.de/) |
| GitLab CI Token | 48xcFyyGmVBiNG3zQ6PJ                                       |
| Description     | sprincl-ci                                                 |
| Tags            | -                                                          |
| Executor        | shell                                                      |

The shell executor was chosen, because it is the most simple one, and the other executors are either not recommended (SSH) or need a Docker, Kubernetes, VirtualBox/Parallels, etc. The shell executor is usually not a good choice as all software needed for the build has to be installed and the build environment is not cleaned after a build. But in our case it is acceptable, because tox automation is used, which creates its own virtual environment.

Since the continuous integration uses tox (a framework for standardized Python testing), it needs to be installed as well. The GitLab runner is running its tasks using the `gitlab-runner` user, so the Python modules have to be installed for that user (`pip` installs the modules into the home directory of the current user).

```sh
sudo apt install python-pip python3-pip
sudo runuser -l gitlab-runner -c 'pip install tox'
sudo runuser -l gitlab-runner -c 'pip3 install tox'
```

If the server does not have Python 3.7 installed, then it can be installed from source. For example for Ubuntu there may be PPAs with newer versions of Python, but for a server it may be a security risk to use unsupported PPAs. Therefore installing from source should be the preferred option.

```sh
# Install the pre-requisites
sudo apt install \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    wget

# Download the Python 3.7 source code
wget https://www.python.org/ftp/python/3.7.4/Python-3.7.4.tar.xz
tar -xf Python-3.7.3.tar.xz
rm Python-3.7.4.tar.xz
cd Python-3.7.4

# Build Python with optimizations
./configure --enable-optimizations
make -j 8

# Install Python (please make sure to use altinstall, because install will override the system Python)
sudo make altinstall
```
