# from api_call import ApiCallTool

# tool = ApiCallTool()
# print(tool.description)
# print(tool.name)
# print(tool.tool_template)
# print(tool.run(args=None))

import requests

url = "https://api.coingecko.com/api/v3/coins/ethereum"

headers = {
    "accept": "application/json",
    "x-cg-demo-api-key": "CG-JKGX3L798t1oFRoV5FJ9ThzD"
}

response = requests.get(url, headers=headers)
data = response.json()

print(response.text)
print(data["market_data"]["current_price"]["usd"])