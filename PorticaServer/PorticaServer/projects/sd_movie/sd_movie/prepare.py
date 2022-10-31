import json
import base64
datas = json.loads(input())
output = json.loads(input())
if len(output) == 1 and output[0]['output_type'] == 'img' and datas['options'].get('init_video', None) is None:
    filename = output[0]['output']
    with open('app/static/' + filename, 'rb') as f:
        content = base64.b64encode(f.read()).decode('utf-8')
        value = {'address': filename, 'content': content}
    print(json.dumps({'init_img': value}))
else:
    print(json.dumps({}))