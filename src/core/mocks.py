class MockAuthHTTPResponse:
    def __init__(self, ok=True, content=""):
        self.ok = ok
        self.text = content
        self.status_code = "Mock"
