export $(xargs <.env)

ray start --head --resources='{"tasks": 100, "rags": 100}' --port 6375 --block
