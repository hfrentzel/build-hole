#! /usr/bin/env python
import json

with open("hole.json") as f:
    hole = json.loads(f.read())

with open("manifest.txt") as f:
    manifest = f.readlines()

release, *files = manifest
for file in files:
    app, version, env = file.strip().split("_", 2)
    if not hole.get(app):
        hole[app] = {}
    if not hole[app].get(version):
        hole[app][version] = {}

    env = env.split(".tar.gz")[0]
    hole[app][version][env] = (
        f"https://github.com/hfrentzel/build-hole/releases/download/{release.strip()}/{file.strip()}"
    )

with open("hole.json", "w") as f:
    f.write(json.dumps(hole, indent=2))