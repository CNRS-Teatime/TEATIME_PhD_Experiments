# Argo workflow creator

This folder contains python scripts using [Hera](https://github.com/argoproj-labs/hera) to create workflows for [Argo Workflows](https://argo-workflows.readthedocs.io/en/latest/).

## Prerequisites

Only python 3.12 has been tested with these script

### Environments variables

The workflows will be created and sent to an existing Argo Workflow instance and namespace. For this purpose you need to set some environment variables before being able to execute the scripts. According to the documentation these are the variables you need to set (Which can be found in the user info page of the Web Frontend).

```bash
export ARGO_SERVER='[INSERT_SERVER_HOSTNAME_HERE]'
export ARGO_HTTP1=true
export ARGO_SECURE=true
export ARGO_BASE_HREF=
export ARGO_TOKEN='[INSERT_TOKEN_HERE]'
export ARGO_NAMESPACE=argo ;# or whatever your namespace is
export KUBECONFIG=/dev/null ;# recommended

# check it works:
argo list
```

### Virtual environment

As usual with python we start by creating a virtual environment and installing the dependencies listed in requirements.txt. All of the following command should be executed inside the `hera\` forlder.

Create virtual environment :

```bash
python3 -m venv .hera
```

Then activate the virtual environment :

### Unix/MacOS

```bash
source {foldername}/bin/activate
```

### Windows

```bash
./{foldername}/bin/activate
```

Finaly you can install the dependencies listed in requirements.txt via this command

```bash
python3 -m pip install -r requirements.txt
```

## Usage

Execute the build.sh script, which will execute each workflow script in the correct order, to build the workflows.

Unix Like :
```bash
chmod +x build.sh
./build.sh
```

Windows user might have to use different commands.