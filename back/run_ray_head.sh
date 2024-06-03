export $(xargs <.env)

ray start --head --port 6375 --metrics-export-port=8080 --num-cpus 0 --num-gpus 0 --dashboard-host 0.0.0.0
