#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for pymolToUMol

"""

import pytest

import pymol
import pickle

import pymolToUMol

@pytest.fixture
def mol_1kx2():
    psefile = "tests/1kx2_HemeVDW_surface.pse"
    with open(psefile, 'rb') as f:
        pse = pickle.load(f)

    return pse['names'][1]

def test_name(mol_1kx2):
    # Check the  molecule name
    assert mol_1kx2[0] == '1kx2'

def test_moleculeRepre(mol_1kx2):
    representations = pymolToUMol.moleculeRepre(mol_1kx2[5][7])
    assert representations == [288, 258]