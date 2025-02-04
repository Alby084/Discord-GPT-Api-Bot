from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv(override=True)

gpt_api_key = os.getenv("GPT_API_KEY")
openrouter_deepseek_api_key = os.getenv("OPENROUTER_DEEPSEEK_API_KEY")

def gpt(model: str, prompt: str, sys_prompt: str, temp: float,):
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

def deepseek(prompt: str, sys_prompt: str, max_retries = 3):
    for attempt in range(max_retries):
        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openrouter_deepseek_api_key}"
                },
                json={
                    "model": "deepseek/deepseek-r1:free",
                    "messages": [
                        {
                            "role": "system",
                            "content": sys_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "provider": {
                        "order": ["Chutes", "Targon", "Azure"],
                        "allow_fallbacks": False
                    },
                    "include_reasoning": True
                }
            )
            
            response_data = response.json()
            print(f"API Response (Attempt {attempt + 1}):", json.dumps(response_data, indent=2))
            
            # Handle 500 errors
            if response.status_code == 500:
                error_message = response_data.get("error", {}).get("message", "Unknown error")
                print(f"Attempt {attempt + 1}/{max_retries}: Got server error: {error_message}")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    continue
                raise Exception(f"Failed after {max_retries} attempts. Last error: {error_message}")
            
            # Check for missing or empty choices
            if not response_data.get("choices"):
                print("No choices in response")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    continue
                raise Exception("No choices in API response after all retries")
            
            message = response_data["choices"][0].get("message", {})
            content = message.get("content")
            
            # Handle empty or missing content
            if not content:
                print("Empty or missing content in response")
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"Waiting {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    continue
                raise Exception("Empty or missing content in response after all retries")
            
            # Check for reasoning
            reasoning = message.get("reasoning")
            if reasoning:
                print("Reasoning:", reasoning.strip())
            
            return content.strip()
            
        except requests.exceptions.RequestException as e:
            print(f"Request error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                continue
            raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error on attempt {attempt + 1}: {str(e)}")
            print(f"Raw response: {response.text}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"Waiting {wait_time} seconds before retrying...")
                time.sleep(wait_time)
                continue
            raise Exception(f"Invalid JSON response after {max_retries} attempts")
            
    raise Exception("All retry attempts failed")
    
     
    # client = OpenAI(
    #     base_url = "https://openrouter.ai/api/v1",
    #     api_key = openrouter_deepseek_api_key
    # )
    # response = client.chat.completions.create(
    #     model = "deepseek/deepseek-r1:free",
    #     messages = [
    #         {
    #             "role": "system",
    #             "content": sys_prompt
    #         },
    #         {
    #             "role": "user",
    #             "content": prompt
    #         }
    #     ],
    #     provider = {
    #         "order": ["Chutes", "Targon", "Azure"],
    #         "allow_fallbacks": False,
    #     },
    #     include_reasoning = True, # Include reasoning in response
    # )
    
    # # Access reasoning if available
    # try:
    #     if hasattr(response.choices[0].message, "reasoning"):
    #         print(response.choices[0].message.reasoning.strip())
    # except AttributeError:
    #     print("No reasoning provided in response")
    
    # output = response.choices[0].message.content.strip()
    # return output

# client = OpenAI(
#   base_url="https://openrouter.ai/api/v1",
#   api_key="<OPENROUTER_API_KEY>",
# )

# completion = client.chat.completions.create(
#   extra_headers={
#     "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
#     "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
#   },
#   model="deepseek/deepseek-r1:free",
#   messages=[
#     {
#       "role": "user",
#       "content": "What is the meaning of life?"
#     }
#   ]
# )
# print(completion.choices[0].message.content)

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