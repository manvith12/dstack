# Torchrun

This provider runs a distributed PyTorch training on multiple nodes. 

You can specify the Python file with the training script, the number of nodes, the version of Python, 
a `requirements.txt` file, environment variables, arguments, which folders to save as output artifacts 
(on the master node), dependencies to other workflows if any, and the resources the workflow needs on each node
(e.g. CPU, GPU, memory, etc).

## Example usage 

### Basic example

=== ".dstack/workflows.yaml"

    ```yaml
    workflows:
      - name: train
        provider: torchrun
        file: "train.py"
        requirements: "requirements.txt"
        artifacts: ["model"]
        nodes: 4
        resources:
          gpu:
            name: "K80"
            count: 4
    ```

Alternatively, you can use this provider from the CLI (without defining your workflow
in the `.dstack/workflows.yaml` file):

```bash
dstack run torchrun train.py --nnodes 4 \
  -r requirements.txt -a model \
  --gpu 4 --gpu-name K80 
```

[//]: # (TODO: Environment variables)

[//]: # (TODO: Resources)

## Workflows file reference

The following arguments are required:

- `file` - (Required) The Python file with the training script, e.g. `"train.py"`

The following arguments are optional:

- `nodes` - (Required) The number of nodes. By default, it's `1`.
- `args` - (Optional) The list of arguments for the Python program
- `before_run` - (Optional) The list of shell commands to run before running the Python file
- `requirements` - (Optional) The path to the `requirements.txt` file
- `version` - (Optional) The major version of Python. By default, it's `3.10`.
- `environment` - (Optional) The list of environment variables 
- `artifacts` - (Optional) The list of folders that must be saved as output artifacts
- [`resources`](#resources) - (Optional) The hardware resources required by the workflow
- `working_dir` - (Optional) The path to the working directory

#### resources

The hardware resources required by the workflow

- `cpu` - (Optional) The number of CPU cores
- `memory` (Optional) The size of RAM memory, e.g. `"16GB"`
- [`gpu`](#gpu) - (Optional) The number of GPUs, their model name and memory
- `shm_size` - (Optional) The size of shared memory, e.g. `"8GB"`
- `interruptible` - (Optional) `true` if the workflow can run on interruptible instances.
    By default, it's `false`.

#### gpu

The number of GPUs, their name and memory

- `count` - (Optional) The number of GPUs
- `memory` (Optional) The size of GPU memory, e.g. `"16GB"`
- `name` (Optional) The name of the GPU model (e.g. `"K80"`, `"V100"`, etc)

## CLI reference

```bash
usage: dstack run torchrun [-h] [-r [REQUIREMENTS]] [-e [ENV]] [-a [ARTIFACT]]
                           [--working-dir [WORKING_DIR]] [-i] [--cpu [CPU]]
                           [--memory [MEMORY]] [--gpu [GPU]]
                           [--gpu-name [GPU_NAME]] [--gpu-memory [GPU_MEMORY]]
                           [--shm-size [SHM_SIZE]] [--nnodes [NNODES]]
                           FILE [ARGS ...]
```

The following arguments are required:

- `FILE` - (Required) The Python file with the training script

The following arguments are optional:

- `--nnodes [NNODES]` - (Optional) The number of nodes. By default, it's `1`.
- `--working-dir [WORKING_DIR]` - (Optional) The path to the working directory
- `-r [REQUIREMENTS]`, `--requirements [REQUIREMENTS]` - (Optional) The path to the `requirements.txt` file
- `-e [ENV]`, `--env [ENV]` - (Optional) The list of environment variables 
- `-a [ARTIFACT]`, `--artifact [ARTIFACT]` - (Optional) A folder that must be saved as output artifact
- `--cpu [CPU]` - (Optional) The number of CPU cores
- `--memory [MEMORY]` - The size of RAM memory, e.g. `"16GB"`
- `--gpu [GPU]` - (Optional) The number of GPUs
- `--gpu-name [GPU_NAME]` - (Optional) The name of the GPU model (e.g. `"K80"`, `"V100"`, etc)
- `--gpu-memory [GPU_MEMORY]` - (Optional) The size of GPU memory, e.g. `"16GB"`
- `--shm-size [SHM_SIZE]` - (Optional) The size of shared memory, e.g. `"8GB"`
- `-i`, `--interruptible` - (Optional) if the workflow can run on interruptible instances.
- `ARGS` - (Optional) The list of arguments for the Python program

[//]: # (TODO: Add --dep argument)

## Source code

[:octicons-arrow-right-24: GitHub](https://github.com/dstackai/dstack/tree/master/providers/torchrun)