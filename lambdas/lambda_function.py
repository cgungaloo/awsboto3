import json

def lambda_handler(event, context):
    # parse query strings
    x = event['queryStringParameters']['x']
    y = event['queryStringParameters']['y']
    op = event['queryStringParameters']['op']
    
    print(f"x:{x}, y:{y}, op:{op}")
    res_body ={}
    res_body['x'] = int(x)
    res_body['y'] = int(y)
    res_body['op'] = op
    res_body['ans'] = multi(res_body['x'],res_body['y'])
    print(res_body)
    
    http_res = {}
    http_res['statusCode'] = 200
    http_res['headers'] = {}
    http_res['headers']['Content-Type'] = 'application/json'
    http_res['body'] = json.dumps(res_body)
    
    return http_res
    
    
def multi(x,y):
    return x * y