class APIError(Exception):
	def __init__(self, str):
		super().__init__(str)

class ConfigurationError (Exception):
	def __init__(self, str):
		super().__init__(str)