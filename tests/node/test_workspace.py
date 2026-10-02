from nablamath.node import Workspace


def test_workspace_projects_are_transactional_and_sorted(tmp_path):
    workspace = Workspace(tmp_path / "workspace.db")
    workspace.set_project("zeta", "a" * 64)
    workspace.set_project("alpha", "b" * 64)
    workspace.set_project("alpha", "c" * 64)
    assert workspace.projects() == (("alpha", "c" * 64), ("zeta", "a" * 64))
    workspace.remove("alpha")
    assert workspace.projects() == (("zeta", "a" * 64),)
