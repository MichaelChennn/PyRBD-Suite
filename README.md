## Recommended Environment

- WSL2 with Ubuntu 22.04
- Python 3.10 or higher
- GCC 11/G++ 11

## Install GCC, G++, CMake

```bash
sudo apt update
```

## Python Environment

```bash
conda create -n pyrbd_suite python=3.10
conda activate pyrbd_suite
pip install --upgrade pip
pip install -r requirements.txt
conda install -c conda-forge gcc_linux-64=11 gxx_linux-64=11
```

## Install CPP Dependencies

```bash
chmod +x build.sh
./build.sh
```

## Run the benchmark
- Get time for availability estimation
```bash
conda activate pyrbd_suite
python benchmark/availability/run_availability_benchmarks.py 
```

- Get time for minimal cut sets evaluation
```bash
python benchmark/mincutsets/run_mincutsets_benchmark.py  
```

## Topology Reference
**Germany_17**: [SNDlib 1.0-survivable network design library](https://sndlib.put.poznan.pl/home.action)