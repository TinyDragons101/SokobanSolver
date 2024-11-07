# Sokoban Solver
This file contains instructions for running the source code.

## Prerequisites
Firstly, you create a python virtual environment (with `conda create` or `python -m venv`) and activate it.
Then, you install all required packages listed in `requirements.txt`.
```sh
pip install -r requirements.txt
```
You should change you current directory to `../Source`:
```sh
cd Source
```
or run the command with prefix path `Source/` in python file name.

## Usage

### Run a search algorithm and print its result to the console
```sh
python test.py [(--method | -m) <algorithm>] [(--level | -l) <input_filename>]
```
**Description**:
* If `--method` or `-m` is given, the specified `<algorithm`> is carried out. If not, *Breadth First Search* is carried out. `<algorithm>` must be `bfs` (*Breadth First Search*), `dfs` (*Depth First Search*), `ucs` (*Uniform Cost Search*) or `astar` (*A\* Search*).
* If `--level` or `-l` is given, the maze is loaded from `<input_filename>`. If not, the maze is loaded from `input-01.txt`

### Run all search algorithms and write their resuls to a file
```sh
python script.py <input_filename> <outpur_filename>
```
**Description**: Run all search algorithms on the maze loaded from `<input_filename>` and write the results to `<output_filename>`.

### Run the GUI
```sh
python main.py
```
**Note**: Whenever `START` a level, if the corresponding output file exists (which is named `output-<ID>.txt`), the program will load the results of all search algorithms from this file, and if not, the program will run `script.py` to get the output file and load from it.