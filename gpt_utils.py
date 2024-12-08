import openai

# Set your OpenAI API key
openai.api_key = "your-openai-api-key"

def query_gpt(prompt):
    """Send a query to GPT-4 and return the response."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']
