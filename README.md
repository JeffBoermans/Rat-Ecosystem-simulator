# COMPBIO-NACO

Project for Computational Biology (2022-2023), 3rd Bachelor Computer Science at the University of Antwerp


<img width="1470" alt="Application Screenshot" src="https://github.com/JeffBoermans/COMPBIO-NACO/assets/60882129/3ca648d5-a545-4cba-8073-833578a583bf">
# Setup

This section is only applicable if you are developing for this repository. The project code specifies its dependencies via the `requirements.txt` file present in the project root. The project root does contain install scripts, but currently only the `install.sh` scipt is guaranteed to work as intended. To install the requirements, run the following commands:

```sh
chmod +x install.sh
./install.sh
```

# Running the Simulation

## For Non-Technical Users

Present in the `build/` folder of this project are pre-built executables which can be used to immediately run the simulation. Download the file for your chosen operating system and simply run it.

* **Linux** : [simulation-linux](/build/simulation-linux)
* **Windows** : [simulation-windows.exe](/build/simulation-windows.exe)
* **MacOS** : Not provided, refer to [the technical section](#for-technical-users)

## For Technical Users

The entry point of the simulation is the [main.py](main.py) file. To run the simulation code manually, execute one of the following commands:

```sh
python main.py
python3 main.py
```

Also provided are `build` scripts that will build an executable of the simulation code, based on the [pyinstaller](https://pyinstaller.org/en/stable/) python module. This means that running the build script will generate an executable appropriate to the OS that the script is run on. Creating an executable for a different OS requires access to the OS in question, to run the build script from. Again note that only the `build.sh` script is currently guaranteed to work.

Note that the circleci config attached to this project, together with the linked circleci project, should automatically update the git repo with up-to-date versions of the executables for some limited number of platforms. These are available in the [build](/build/) directory. The circleci CI is run on every commit, so every change that produces a different executable binary than the ones in the repo will result in updated executables.
