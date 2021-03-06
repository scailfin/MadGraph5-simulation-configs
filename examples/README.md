# Drell-Yan Production Example in MadGraph

```
docker pull scailfin/madgraph5-amc-nlo:mg5_amc3.1.0
```

then

```
bash run_example.sh
```

For plotting, create a Python 3 virtual environment, activate it, and then from the top level of the project pip install the dependencies

```
python -m pip install -r requirements.txt
```

Then plot the results of the example with

```
python plot_mass_spectrum.py
```

## Notes

### MadGraph tutorials

- [Notes for Madgraph tutorial for NIU PHYS 474/790](https://www.niu.edu/spmartin/madgraph/madtutor.html)
- [CMS Madgraph and Delphes Tutorial](https://twiki.cern.ch/twiki/bin/view/CMSPublic/MadgraphTutorial)
