class APIError(Exception):
	code = None
	def __init__(self, str, endpoint):
		super().__init__(str)
		self.endpoint = endpoint