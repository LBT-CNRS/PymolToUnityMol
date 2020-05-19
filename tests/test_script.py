#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for pymolToUMol

"""

import pytest

import pymol
import pickle

from PymolToUnityMol import pymolToUMol

PSE_FILE="tests/1kx2_HemeVDW_surface.pse"

@pytest.fixture
def mol_1kx2():
    """
    Fixture function using in all tests to retrieve the data in
    the pse file.
    """
    with open(PSE_FILE, 'rb') as f:
        pse = pickle.load(f)

    return pse['names'][1]


def test_name(mol_1kx2):
    """
    Ensure the file is read correctly.
    """
    # Check the  molecule name
    assert mol_1kx2[0] == '1kx2'


def test_moleculeRepre(mol_1kx2):
    """
    Test the function moleculeRepre with molecule 1kx2
    Test the representation ids.
    """
    representations = pymolToUMol.moleculeRepre(mol_1kx2[5][7])
    assert representations == [288, 258]


def test_atomidAndColor(mol_1kx2):
    """
    Test the function atomidAndColor with molecule 1kx2
    Ensure the atomid and their color matches.
    """
    all_atoms = mol_1kx2[5][7]
    atom_colors = pymolToUMol.atomidAndColor(all_atoms, 288)

    assert atom_colors[0] == (1, 27)
    assert atom_colors[100] == (101, 28)
    assert atom_colors[284] == (285, 29)


def test_representation(mol_1kx2):
    """
    Test the match between representation's id and the representation's name in Unitymol
    """
    repr1 = pymolToUMol.representation(288)
    assert repr1 == ['cartoon', 'mesh']
    repr2 = pymolToUMol.representation(258)
    assert repr2 == ['spheres', 'mesh']


def test_numberToAtomid():
    """
    Test the match between the atomid in the pse and
    the atomid in the pdb.
    """
    with open(PSE_FILE, 'rb') as f:
        pse = pickle.load(f)
    heme_selection = pse['names'][2]
    dic_atoms = pymolToUMol.numberToAtomid(pse, heme_selection[5][0][0])
    assert dic_atoms[0] == 1
    assert dic_atoms[34] == 35
    assert dic_atoms[1120] == 1121
