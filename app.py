import chainlit as cl
from openai import OpenAI
import base64
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["BASE_API_URL"] = os.getenv("BASE_API_URL", "https://api.openai.com/v1")
model = "gpt-3.5-turbo-1106"
model_vision = "gpt-4-vision-preview"
   
def process_images(msg: cl.Message):
    # Processing images exclusively
    images = [file for file in msg.elements if "image" in file.mime]

    # Accessing the bytes of a specific image
    image_bytes = images[0].content # take the first image just for demo purposes

    # check the size of the image, max 1mb
    if len(image_bytes) > 1000000:
        return "too_large"
    
    # we need base64 encoded image
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    return image_base64

async def process_stream(stream, msg: cl.Message):
    for part in stream:
            if token := part.choices[0].delta.content or "":
                await msg.stream_token(token)

def handle_vision_call(msg, image_history):
    image_base64 = None
    image_base64 = process_images(msg)
    if image_base64 == "too_large":
        return "too_large"
    
    if image_base64:
        # add the image to the image history
        image_history.append(
        {
            "role": "user",
            "content": [
                    {"type": "text", "text": msg.content},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}",
                            "detail": "low"
                        }
                    },
                ],
            }
        )
        stream = gpt_vision_call(image_history)

        return stream

async def gpt_call(message_history: list = []):
    client = OpenAI(base_url=os.environ["BASE_API_URL"])

    stream = client.chat.completions.create(
        model=model,
        messages=message_history,
        stream=True,
    )
    return stream

def gpt_vision_call(image_history: list = []):
    client = OpenAI(base_url=os.environ["BASE_API_URL"])
  
    stream = client.chat.completions.create(
        model=model_vision,
        messages=image_history,
        max_tokens=350,
        stream=True,
    )

    return stream

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant. You are made by GPT-3.5-turbo-1106, the latest version developed by Openai. You do not have the ability to receive images, but if the user uploads an image with the message, GPT-4-vision-preview will be used. So if a user asks you if you have the ability to analyze images, you can tell them that. And tell him that at the bottom left (above the text input) he has a button to upload images, or he can drag it to the chat, or he can just copy paste the input"}],
    )
    cl.user_session.set("image_history", [{"role": "system", "content": "You are a helpful assistant. You are developed with GPT-4-vision-preview, if the user uploads an image, you have the ability to understand it. For normal messages GPT-3.5-turbo-1106 will be used, and for images you will use it. If the user asks about your capabilities you can tell them that."}])
 

@cl.on_message
async def on_message(msg: cl.Message):
    message_history = cl.user_session.get("message_history")
    image_history = cl.user_session.get("image_history")
    
    stream_msg = cl.Message(content="") 
    stream = None

    if msg.elements:
        stream = handle_vision_call(msg, image_history)
        if stream == "too_large":
            return await cl.Message(content="Image too large, max 1mb").send()

    else:
        # add the message in both to keep the coherence between the two histories
        message_history.append({"role": "user", "content": msg.content})
        image_history.append({"role": "user", "content": msg.content})
        
        stream = await gpt_call(message_history)
    
    if stream:
        await process_stream(stream, msg=stream_msg)
        message_history.append({"role": "system", "content": stream_msg.content})
        image_history.append({"role": "system", "content": stream_msg.content})

    return stream_msg.content
