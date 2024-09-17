export $(xargs <.env)
# It runs a Ray cluster on the local machine with 1 node that acts as the head node and 1 worker node.
ray start --head --port 6375 --resources='{"tasks": 100, "rags": 100, "ai_components": 100}' --dashboard-host 0.0.0.0  --block
