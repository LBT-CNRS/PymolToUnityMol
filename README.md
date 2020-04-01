# PymolToUnityMol

Convert pymol session file (.pse) to UnityMol commands

## Requirements

- Python 2.x
- Pymol python library

## How to run

```bash
$ python2 pymolToUMol.py myPymolSession.pse > myUMolSession.py
```

Then import the ```myUMolSession.py``` file in UnityMol.

You should see the same representations (if they exist in UnityMol) with the same coloring, and all the selections done in Pymol.

## Limitations

- For now, this only works for files fetched from the PDB.

## Contribute

Pull requests are more than welcome !

## License

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)


## Result

![alt tag](https://i.imgur.com/PEpEei2.png)

![alt tag](https://i.imgur.com/0yT44yu.png)
