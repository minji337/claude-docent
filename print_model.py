import anthropic
from pprint import pprint

client = anthropic.Anthropic()
pprint(client.models.list(limit=20).model_dump()['data'])