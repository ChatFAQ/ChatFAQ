FROM ubuntu:22.04

RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh
RUN bash ~/miniconda.sh -b -p $HOME/miniconda

# Create the environment
RUN /root/miniconda/bin/conda create -n vllm_venv python=3.10 -y

RUN /root/miniconda/envs/vllm_venv/bin/pip install https://download.pytorch.org/whl/cu118/torch-2.0.1%2Bcu118-cp310-cp310-linux_x86_64.whl

# Use the full path to the pip in the created environment
RUN /root/miniconda/envs/vllm_venv/bin/pip install vllm

# Update PATH so that the vllm_venv environment is the default
ENV PATH="/root/miniconda/envs/vllm_venv/bin:${PATH}"

ENV PORT=5000
ENV SWAP_SPACE=2
ENV MODEL=facebook/opt-125m


COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
