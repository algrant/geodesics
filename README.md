Currently just a simple little program to generate & view geodesic vases.


### setup steps
```
  conda create --name geodesics
  conda activate geodesics

  conda install -c anaconda jupyter
  conda install numpy
  conda install -c conda-forge meshplot
```

### install bezier...
conda failed me here, I ended up doing...

```
  ./miniconda3/envs/geodesics/bin/python -m pip install --upgrade bezier
```