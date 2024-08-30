export $(xargs <.env)

ray start --address=back:6375 --resources='{"tasks": 100, "ai_components": 100}' --block
