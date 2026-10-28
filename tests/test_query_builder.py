from app.utils.query_builder import build_boolean_query
def test_query_builder():
    assert build_boolean_query("Fresher").startswith("site:linkedin.com/in/")
def test_custom_keyword():
    assert '"AI engineer"' in build_boolean_query("Fresher", "AI engineer")
