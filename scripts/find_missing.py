#! /usr/bin/env python
import json

import yaml

with open("build.yaml") as f:
    builds = yaml.load(f.read(), Loader=yaml.Loader)

with open("hole.json") as f:
    hole = json.loads(f.read())

missing = []


def add_to_missing(name, spec, env):
    missing_spec = {
        "name": name,
        "type": spec["type"],
        "repo": spec["repo"],
        "version": spec["version"],
        "env": env,
    }
    if env == "aarch64-linux-22.04":
        missing_spec["runner"] = "ubuntu-22.04"
        if spec["type"] == "rust":
            missing_spec["target"] = "aarch64-unknown-linux-gnu"
        elif spec["type"] == "go":
            missing_spec["goos"] = "linux"
            missing_spec["goarch"] = "arm64"
    else:
        missing_spec["runner"] = "ubuntu-20.04"
        if spec["type"] == "rust":
            missing_spec["target"] = "x86_64-unknown-linux-musl"
        elif spec["type"] == "go":
            missing_spec["goos"] = "linux"
            missing_spec["goarch"] = "amd64"

    if spec.get("exe_name"):
        missing_spec["exe_name"] = spec["exe_name"]
    if spec.get("package"):
        missing_spec["package"] = spec["package"]
    if spec.get("tag"):
        missing_spec["tag"] = spec["tag"].format(version=spec["version"])
    if spec.get("flags"):
        missing_spec["flags"] = spec["flags"]

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
