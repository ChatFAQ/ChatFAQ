export $(xargs <.env)

ray start --address=back:6375 --resources='{"tasks": 100, "rags": 100}' --block
