#! /usr/bin/env python
import json

import yaml

with open("build.yaml") as f:
    builds = yaml.load(f.read(), Loader=yaml.Loader)

with open("hole.json") as f:
    hole = json.loads(f.read())

missing = []


def add_to_missing(name, spec, env):
    if env in spec.get("exclude", []):
        return

    missing_spec = {
        "name": name,
        "type": spec["type"],
        "repo": spec["repo"],
        "version": spec["version"],
        "env": env,
    }
    if env == "aarch64-linux-22.04":
        missing_spec["runner"] = "ubuntu-22.04-arm"
        missing_spec["goos"] = "linux"
        missing_spec["goarch"] = "arm64"
        if spec["type"] == "cargo":
            missing_spec["target"] = "aarch64-unknown-linux-gnu"
    elif env == "x86_64-linux-22.04":
        missing_spec["runner"] = "ubuntu-22.04"
        missing_spec["goos"] = "linux"
        missing_spec["goarch"] = "amd64"
        if spec["type"] == "cargo":
            missing_spec["target"] = "x86_64-unknown-linux-musl"
    else:
        missing_spec["runner"] = "windows-2022"
        missing_spec["goos"] = "windows"
        missing_spec["goarch"] = "amd64"
        if spec["type"] == "cargo":
            missing_spec["target"] = "x86_64-pc-windows-msvc"

    if spec.get("exe_name"):
        missing_spec["exe_name"] = spec["exe_name"]
    if spec.get("package"):
        missing_spec["package"] = spec["package"]
    if spec.get("package_windows") and env == "x86_64-windows":
        missing_spec["package"] = spec["package_windows"]
    if spec.get("prebuild"):
        missing_spec["prebuild"] = spec["prebuild"]
    if spec.get("prebuild_linux") and env != "x86_64-windows":
        missing_spec["prebuild"] = spec["prebuild_linux"]
    if spec.get("tag"):
        missing_spec["tag"] = spec["tag"].format(version=spec["version"])
    if spec.get("flags"):
        if isinstance(spec["flags"], list):
            missing_spec["flags"] = " ".join(spec["flags"])
        else:
            missing_spec["flags"] = spec["flags"]
    if spec.get("entrypoint"):
        missing_spec["entrypoint"] = spec["entrypoint"]
    if spec.get("working-directory"):
        missing_spec["working_dir"] = spec["working-directory"]
    if spec.get("recurse"):
        missing_spec["recurse"] = spec["recurse"]
    if not spec.get("no_verify"):
        missing_spec["verify"] = True

    missing.append(missing_spec)


for app, spec in builds["apps"].items():
    app_hole = hole.get(app, {}).get(spec["version"])
    if not app_hole:
        for env in builds["envs"]:
            if env not in spec.get("exclude", []):
                add_to_missing(app, spec, env)
        continue
    for env in builds["envs"]:
        if env not in app_hole:
            add_to_missing(app, spec, env)

print(json.dumps(missing))
