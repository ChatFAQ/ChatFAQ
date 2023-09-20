To create the docker image, run the following command from the root of the repository:
```bash
sudo docker build -t vllm .
```

To run the docker image, run the following command from the root of the repository:
```bash
sudo docker run --gpus all -it --rm --shm-size=8g -p 5000:5000 vllm
```

Or run the following command to run the docker image with a HuggingFace API key for access to private models:
```bash
sudo docker run --gpus all -it --rm --shm-size=8g -p 5000:5000 -e HUGGINGFACE_KEY=$HUGGINGFACE_KEY vllm
```