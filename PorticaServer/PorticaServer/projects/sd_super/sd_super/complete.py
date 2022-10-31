import json
values = json.loads(input())
options = values.get('options', {})
print(json.dumps({'output_type': 'json', 'output': options.get('tasks', {})}))