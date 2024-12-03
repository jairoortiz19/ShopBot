import os
from openai import OpenAI
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Mock product catalog
PRODUCT_CATALOG = {
    "eco_bottle": {
        "id": "P001",
        "name": "EcoFriendly Water Bottle",
        "description": "1L sustainable water bottle made from recycled materials",
        "price": 24.99,
        "stock": 150
    },
    "smart_watch": {
        "id": "P002",
        "name": "SmartFit Watch Pro",
        "description": "Fitness tracker with heart rate monitoring and GPS",
        "price": 199.99,
        "stock": 75
    },
    "laptop_bag": {
        "id": "P003",
        "name": "Urban Commuter Laptop Bag", 
        "description": "Waterproof 15-inch laptop bag with multiple compartments",
        "price": 89.99,
        "stock": 200
    },
    "wireless_earbuds": {
        "id": "P004",
        "name": "SoundPro Wireless Earbuds",
        "description": "Noise-cancelling earbuds with 24-hour battery life",
        "price": 149.99,
        "stock": 0
    },
    "yoga_mat": {
        "id": "P005", 
        "name": "Premium Yoga Mat",
        "description": "Non-slip eco-friendly yoga mat with carrying strap",
        "price": 49.99,
        "stock": 100
    }
}

class EcommerceAssistant:
    def __init__(self):
        self.client = OpenAI()
        self.assistant = self._create_assistant()
        self.thread = self._create_thread()
        
    def _create_assistant(self):
        """Create an OpenAI Assistant with product-related functions"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Get detailed information about a product",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "The name of the product to look up"
                            }
                        },
                        "required": ["product_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "check_stock",
                    "description": "Check if a product is in stock",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "The name of the product to check stock for"
                            }
                        },
                        "required": ["product_name"]
                    }
                }
            }
        ]
        
        assistant = self.client.beta.assistants.create(
            name="ShopBot",
            instructions="""You are a helpful e-commerce assistant. Help users find product information 
            and check stock availability. Use the provided functions to fetch accurate product data. 
            Be friendly and informative in your responses.""",
            tools=tools,
            model="gpt-4o"
        )
        return assistant

    def _create_thread(self):
        """Create a new conversation thread"""
        return self.client.beta.threads.create()

    def get_product_info(self, product_name):
        """Retrieve product information from the catalog"""
        # Search case-insensitive
        for key, product in PRODUCT_CATALOG.items():
            if product_name.lower() in product["name"].lower():
                return json.dumps(product)
        return json.dumps({"error": "Product not found"})

    def check_stock(self, product_name):
        """Check if a product is in stock"""
        # Search case-insensitive
        for key, product in PRODUCT_CATALOG.items():
            if product_name.lower() in product["name"].lower():
                stock = product["stock"]
                return json.dumps({"available": stock > 0, "quantity": stock})
        return json.dumps({"error": "Product not found"})

    def process_message(self, user_message):
        """Process user message and get assistant's response"""
        # Add user message to thread
        self.client.beta.threads.messages.create(
            thread_id=self.thread.id,
            role="user",
            content=user_message
        )

        # Create a run
        run = self.client.beta.threads.runs.create(
            thread_id=self.thread.id,
            assistant_id=self.assistant.id
        )

        # Wait for run to complete
        while True:
            run_status = self.client.beta.threads.runs.retrieve(
                thread_id=self.thread.id,
                run_id=run.id
            )
            
            if run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    if function_name == "get_product_info":
                        output = self.get_product_info(arguments["product_name"])
                    elif function_name == "check_stock":
                        output = self.check_stock(arguments["product_name"])
                    
                    tool_outputs.append({
                        "tool_call_id": tool_call.id,
                        "output": output
                    })
                
                self.client.beta.threads.runs.submit_tool_outputs(
                    thread_id=self.thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
            
            elif run_status.status == "completed":
                break
            
            elif run_status.status in ["failed", "cancelled", "expired"]:
                return f"Error: Run ended with status {run_status.status}"

        # Get the latest assistant message
        messages = self.client.beta.threads.messages.list(
            thread_id=self.thread.id
        )
        return messages.data[0].content[0].text.value

def main():
    assistant = EcommerceAssistant()
    print("Welcome to ShopBot! Ask me about our products. (Type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
            
        response = assistant.process_message(user_input)
        print(f"\nShopBot: {response}")

if __name__ == "__main__":
    main()