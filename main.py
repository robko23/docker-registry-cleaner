#!/usr/bin/env python
import smtplib, ssl
import socket
from email.mime.text import MIMEText
import subprocess

# Which registry to use
REGISTRY = "<fill>"

# How many versions to keep
KEEP_LATEST = 7

REGISTRY_CONTAINER_NAME = "registry"

SMTP_SERVER = '<fill>'
SMTP_PORT = 465
SMTP_USER = "<fill>"
SMTP_PASSWORD = "<fill>"
SMTP_SERVICE_ADDRESS = "<fill>"

removed_tags = 0

def execute_regctl(cmd: str) -> str:
    return subprocess.check_output(f"./regctl {cmd}", shell=True, universal_newlines=True)

def garbage_collect_registry():
    print("Running garbage collection")
    subprocess.check_output(f"docker exec {REGISTRY_CONTAINER_NAME} /bin/registry garbage-collect /etc/docker/registry/config.yml --delete-untagged")
    print("Restating container")
    subprocess.check_output(f"docker restart {REGISTRY_CONTAINER_NAME}")

def load_repos():
    output = execute_regctl(f"repo ls {REGISTRY}").strip()
    output = output.split('\n')
    return output

def load_tags(repo: str, remove_latest: bool = True):
    output = execute_regctl(f"tag ls {REGISTRY}/{repo}")
    versions = output.split('\n')
    versions.remove("")
    if remove_latest:
        versions.remove("latest")
    return versions

def clear_repo(repo: str):
    tags = load_tags(repo)
    to_be_removed = tags[::-1][KEEP_LATEST:]
    keep = tags[::-1][:KEEP_LATEST]
    for tag in keep:
        print(f"Keeping {repo}:{tag}")
    for tag in to_be_removed:
        print(f"Removing {repo}:{tag}")
        remove_tag(repo, tag)
    pass

def remove_tag(repo: str, tag: str):
    global removed_tags
    digest = execute_regctl(f"image digest --list {REGISTRY}/{repo}:{tag}").strip()
    print(f"Deleting {digest} [{tag}]")
    execute_regctl(f"manifest rm {REGISTRY}/{repo}@{digest}")
    removed_tags = removed_tags + 1
    pass

def send_mail(subj: str, body: str):
    context = ssl.create_default_context()
    msg = MIMEText(body)
    msg["From"] = SMTP_USER
    msg["To"] = SMTP_SERVICE_ADDRESS
    msg["Subject"] = f"[Registry Cleaner {socket.gethostname()}] {subj}"
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(from_addr=SMTP_USER, to_addrs=SMTP_SERVICE_ADDRESS, msg=msg.as_string())
    pass

def main():
    global removed_tags
    try:
        repos = load_repos()
        for repo in repos:
            clear_repo(repo)
        garbage_collect_registry()
        send_mail(f"Successfully cleaned {removed_tags} tags", f"Successfully cleaned {removed_tags} tags")
    except Exception as e:
        send_mail(f"Exception!", str(e))
        pass
    pass

if __name__ == "__main__":
    main()
