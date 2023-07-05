# model-viz

## Description
`model-viz` is a tool for visualizing the output from the PF/PMCMC models.
## How to Install
First, clone the repository:
```
git clone git@github.com:patelvyom/model-viz.git
```
Then, create a new `miniconda` environment and installed the required packages via `pip`:
```
conda create -n model-viz python=3.10
conda activate model-viz
pip3 install -r requirements.txt
```

## How to Use
The app utilises the `dash` package to create a web app. To run the app, run the following command in the terminal:
```
python3 main.py /path/to/hdf5/file
```
The web app will then be able to be accessed at a local host address.
