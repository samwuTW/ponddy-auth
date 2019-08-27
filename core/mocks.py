class MockAuthHTTPResponse():
    def __init__(self, ok=True, content=''):
        self.ok = ok
        self.content = content
        self.status_code = 'Mock'
