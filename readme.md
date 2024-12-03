# E-commerce AI Assistant

AI-powered e-commerce assistant using OpenAI's Assistants API to handle product queries and inventory checks.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file in project root
2. Add OpenAI API key:
```
OPENAI_API_KEY=your_api_key_here
```

⚠️ IMPORTANT: Never commit your API key to GitHub!

## Usage

Run the assistant:
```bash
python ecommerce_assistant.py
```

Example queries:
- "Tell me about the EcoFriendly Water Bottle"
- "Is the SmartFit Watch Pro in stock?"
- "What's the price of wireless earbuds?"

## Features
- Product information lookup
- Stock availability checking
- Real-time conversation processing
- Mock product catalog with 5 products
