# CITS5506 Project

## Requirements

* A Raspberry Pi.
* A device that is capable of running `Miniconda` and `Flask` with a browser that supports [Notifications API](https://developer.mozilla.org/en-US/docs/Web/API/Notifications_API#browser_compatibility).
* They must be connected to the same private network.

## Setup

### Smart Doorbell (Run on Raspberry Pi)

Update the `USER_ADDR_INFO` constant in [helper.py](helper.py) with the private IP address of the computer that will be used to run the user code. Find the private IP address of the Raspberry Pi.

```bash
hostname -I
```

Install dependencies and run the doorbell code.

```bash
pip install vlc
python doorbell.py
```

### User Interface (Run on any device)

Update the `DOORBELL_ADDR_INFO` constant in [helper.py](helper.py) with the private IP address of the Raspberry Pi. Find the private IP address of the computer.

```bash
ifconfig | egrep 'inet .* broadcast'
```

List all the virtual environments on your system.

```bash
conda env list
```

If you see the error messsage `command not found` go install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

Otherwise check the list of virtual environments on your system and make sure the name `iot` does not exist.

Then create a new virtual environment called `iot` with all the dependencies installed and activate it.

```bash
conda env create --file iot.yml
conda activate iot
```

If it already exists just use another name that is not taken.

```bash
mv iot.yml name_not_taken.yml
conda env create --file name_not_taken.yml
conda activate name_not_taken
```

Run the user code.

```bash
python user.py
```

Open <http://localhost:5000/> to view the user interface.
