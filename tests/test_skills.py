from nutricion.agents.skills import load_skill


def test_skills_load_without_frontmatter():
    for name in ("researching-ai", "evaluating-user"):
        text = load_skill(name)
        assert text.startswith("#")
        assert "name:" not in text.splitlines()[0]
