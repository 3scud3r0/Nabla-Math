from fractions import Fraction
from nablamath.math.linear_algebra import Matrix, identity


def test_exact_matrix_product_determinant_and_rank():
    matrix = Matrix(((1, 2), (3, 4)))
    assert matrix @ identity(2) == matrix
    assert matrix.determinant() == -2
    reduced, rank = matrix.echelon()
    assert reduced == identity(2) and rank == 2


def test_singular_rectangular_rank():
    matrix = Matrix(((1, 2, 3), (2, 4, 6)))
    assert matrix.echelon()[1] == 1
    assert matrix.transpose().shape == (3, 2)
