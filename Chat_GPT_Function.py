from openai import OpenAI
from dotenv import load_dotenv
import os
import openrouter

load_dotenv(override=True)

gpt_api_key = os.getenv("GPT_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

def gpt(model: str, prompt: str, sys_prompt: str, temp: float):
    if model == "deepseek":
        return deepseek(prompt, sys_prompt, temp)
    client = OpenAI(api_key= gpt_api_key)
    response = client.chat.completions.create(
        model = model,
        messages=[
            {
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature = temp,
        # max_tokens=64,
        top_p=1
    )
    output = response.choices[0].message.content.strip()
    return output

def deepseek(prompt: str, sys_prompt: str, temp: float):
    client = openrouter.Client(api_key=deepseek_api_key)
    response = client.chat.create(
        prompt=prompt,
        system_prompt=sys_prompt,
        temperature=temp
    )
    output = response['choices'][0]['message']['content'].strip()
    return output

def dalle3(prompt: str, quality: str, size: str, style: str):
    client = OpenAI(api_key= gpt_api_key)
    response = client.images.generate(
        model = "dall-e-3",
        prompt = prompt,
        size = size,
        quality = quality,
        style = style,
        n=1,
        )
    image_url = response.data[0].url
    return image_url

def dalle2(prompt: str, size: str):
    client = OpenAI(api_key= gpt_api_key)
    response = client.images.generate(
        model = "dall-e-2",
        prompt = prompt,
        size = size,
        n=1,
        )
    image_url = response.data[0].url
    return image_url
