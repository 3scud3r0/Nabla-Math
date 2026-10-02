import math
from fractions import Fraction
import pytest
from nablamath.math.arithmetic import evaluate, expand_rational, convergents
from nablamath.math.analysis import aitken_delta_squared, cauchy_tail_bound, monotonicity, nth_roots, partial_sums
from nablamath.math.equations import integrate
from nablamath.math.probability import MarkovChain
from nablamath.math.statistics import posterior
from nablamath.math.geometry import Point2, contains_convex, convex_hull
from nablamath.math.control import DiscreteLinearSystem
from nablamath.math.linear_algebra import Matrix
from nablamath.math.operations_research import MM1
from nablamath.math.cryptography import caesar, vigenere


def test_continued_fraction_roundtrip():
    value=Fraction(415,93);terms=expand_rational(value)
    assert terms==(4,2,6,7) and evaluate(terms)==value
    assert convergents(terms)[-1]==value


def test_sequence_diagnostics_and_complex_roots():
    sums=partial_sums(lambda n: 1/2**(n+1),10)
    assert monotonicity(sums)=="nondecreasing" and cauchy_tail_bound(sums,3)>0
    assert len(aitken_delta_squared(sums))==8
    roots=nth_roots(1+0j,4)
    assert all(abs(root**4-1)<1e-10 for root in roots)


def test_rk4_exponential_growth():
    trajectory=integrate(lambda t,state:(state[0],),(1.0,),0,1,100)
    assert trajectory[-1][1][0]==pytest.approx(math.e,rel=1e-8)


def test_markov_and_bayes_exact():
    chain=MarkovChain(("sun","rain"),{("sun","sun"):Fraction(3,4),("sun","rain"):Fraction(1,4),
                                           ("rain","sun"):Fraction(1,2),("rain","rain"):Fraction(1,2)})
    assert chain.step({"sun":1,"rain":0})=={"sun":Fraction(3,4),"rain":Fraction(1,4)}
    assert posterior({"H":Fraction(1,2),"T":Fraction(1,2)},{"H":Fraction(3,4),"T":Fraction(1,4)})=={"H":Fraction(3,4),"T":Fraction(1,4)}


def test_convex_hull_control_queue_and_classical_ciphers():
    points=(Point2(0,0),Point2(1,0),Point2(1,1),Point2(0,1),Point2(Fraction(1,2),Fraction(1,2)))
    hull=convex_hull(points);assert len(hull)==4 and contains_convex(hull,Point2(Fraction(1,2),Fraction(1,2)))
    system=DiscreteLinearSystem(Matrix(((1,),)),Matrix(((1,),)))
    assert system.step(Matrix(((2,),)),Matrix(((3,),)))==Matrix(((5,),))
    queue=MM1(2,3);assert queue.expected_system_size==2 and queue.stationary_probability(0)==pytest.approx(1/3)
    assert caesar("Abc!",3)=="Def!"
    encrypted=vigenere("ATTACK","LEMON");assert vigenere(encrypted,"LEMON",decrypt=True)=="ATTACK"
