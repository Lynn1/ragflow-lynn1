# ragflow-lynn1

########### 欢迎使用知识库 ############

  This is a branch forked from "[infiniflow/ragflow](https://github.com/infiniflow/ragflow)",

  where Lynn1 made some bug fixes and customizations.

########################################

## 📝 Prerequisites

- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1  [Install Docker Engine](https://docs.docker.com/engine/install/).
- Ensure `vm.max_map_count` >= 262144:

  ```bash
  # To check the value of `vm.max_map_count`:
  sysctl vm.max_map_count

  # Reset `vm.max_map_count` to a value at least 262144 if it is not.
  sudo sysctl -w vm.max_map_count=262144

  # or: set permanent change in `/etc/sysctl.conf`
  vm.max_map_count=262144
  ```
- Install a virtual environment, , ensuring that Anaconda or Miniconda is installed:

  ```bash
  git clone https://github.com/infiniflow/ragflow.git
  cd ragflow/

  conda create -n ragflow python=3.11.0
  conda activate ragflow
  pip install -r requirements.txt

  # If your CUDA version is higher than 12.0, run the following additional commands:
  pip uninstall -y onnxruntime-gpu
  pip install onnxruntime-gpu --extra-index-url https://aiinfra.pkgs.visualstudio.com/PublicPackages/_packaging/onnxruntime-cuda-12/pypi/simple/

  # Setting huggingface mirror in ~/.bashrc
  export HF_ENDPOINT=https://hf-mirror.com
  ```
- Check the configuration files, ensuring that:

  - The settings in **docker/.env** match those in **conf/service_conf.yaml**.
  - The IP addresses and ports for related services in **service_conf.yaml** match the local machine IP and ports exposed by the container.
  - Add the following line to `/etc/hosts` to resolve all hosts specified in **docker/.env** to `127.0.0.1`:
    ```
    127.0.0.1       es01 infinity mysql minio redis
    x.x.x.x(your ollama server ip)         localllm
    ```

## 🛠️ Launch service from source

To launch the service from source:

```bash
# Launch the database services (MinIO, Elasticsearch, Redis, and MySQL):
docker compose -f docker/docker-compose-base.yml up -d

# Launch backend service: 
conda activate ragflow
export PYTHONPATH=./ 
python api/ragflow_server.py
python rag/svr/task_executor.py

# Launch frontend service: (# Update proxy.target to http://127.0.0.1:9380 in `.umirc.ts`)
cd web
npm install --registry=https://registry.npmmirror.com --force
npm run dev 

```

To stop the service and clean all data:

```bash
# stop docker:
docker compose -f docker/docker-compose-base.yml down

# delete user data:
docker volume rm $(docker volume ls -q)
```
