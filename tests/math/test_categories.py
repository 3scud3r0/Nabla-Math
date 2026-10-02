import pytest
from nablamath.math.category_theory import Functor, NaturalTransformation, discrete_category


def test_identity_functor_and_natural_identity():
    category = discrete_category(("A", "B"))
    functor = Functor(category, category, {"A": "A", "B": "B"}, {"id:A": "id:A", "id:B": "id:B"})
    transformation = NaturalTransformation(functor, functor, {"A": "id:A", "B": "id:B"})
    assert transformation.components["A"] == "id:A"


def test_functor_must_preserve_identity():
    category = discrete_category(("A", "B"))
    with pytest.raises(ValueError):
        Functor(category, category, {"A": "A", "B": "B"}, {"id:A": "id:B", "id:B": "id:A"})
