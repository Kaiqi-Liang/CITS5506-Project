# CITS5506-Project

## Setup

List all the virtual environments on your system.

```bash
conda env list
```

If you see the error messsage `command not found` go install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

Otherwise check the list of virtual environments on your system and make sure the name `iot` does not exist.

Then create a new virtual environment called `iot` with all the dependencies installed and activate it.

```bash
conda env create --file iot.yaml
conda activate iot
```

If it already exists just use another name that is not taken.

```bash
mv iot.yaml name_not_taken.yml
conda env create --file name_not_taken.yml
conda activate name_not_taken
```

Run the server.

```bash
python user.py
```

Open <http://localhost:5000/> to view the user interface.
