import requests
from tool_interface import Tool
import json

class CryptoPriceTool(Tool):

    @property
    def name(self):
        return "crypto_price_getter"
    
    @property
    def description(self):
        return "A tool that will retrieve the latest price for a specified cryptocurrency, along with additional information. Use this tool if the user requests current information about a specific cryptocurrency."
    
    @property
    def tool_template(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "required": ["coin_name"],
                    'properties': {
                        "coin_name": {
                            "type": "string",
                            "description": "The name of the cryptocurrency that data needs to be gathered for. The name of the cryptocurrency specified by the user."
                        }
                    }
                }
            }
        }
    
    def run(self, args):
        name = args['coin_name'].lower()

        url = f"https://api.coingecko.com/api/v3/coins/{name}"
        headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": "CG-JKGX3L798t1oFRoV5FJ9ThzD"
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        tool_data = {
            "current_price": data["market_data"]["current_price"]["usd"],
            "market_cap": data["market_data"]["market_cap"]["usd"],
            "24_hour_volume": data["market_data"]["total_volume"]["usd"],
            "24_hour_high": data["market_data"]["high_24h"]["usd"],
            "24_hour_low": data["market_data"]["low_24h"]["usd"]
        }
        print(data["market_data"]["current_price"]["usd"])
        print(tool_data)
        return json.dumps(tool_data)