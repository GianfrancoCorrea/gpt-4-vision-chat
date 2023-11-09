import chainlit as cl
from openai import OpenAI
from langsmith.run_helpers import traceable
from langsmith_config import setup_langsmith_config
import base64
import os

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
model = "gpt-4-1106-preview"
model_vision = "gpt-4-vision-preview"
setup_langsmith_config()
    
def process_images(msg: cl.Message):
    # Processing images exclusively
    images = [file for file in msg.elements if "image" in file.mime]

    # Accessing the bytes of a specific image
    image_bytes = images[0].content # take the first image just for demo purposes
    
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
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    },
                ],
            }
        )
        stream = gpt_vision_call(image_history)
        return stream

@traceable(run_type="llm", name="gpt 4 turbo call")
async def gpt_call(message_history: list = []):
    client = OpenAI()

    stream = client.chat.completions.create(
        model=model,
        messages=message_history,
        stream=True,
    )
    
    return stream

@traceable(run_type="llm", name="gpt 4 turbo vision call")
def gpt_vision_call(image_history: list = []):
    client = OpenAI()
  
    stream = client.chat.completions.create(
        model=model_vision,
        messages=image_history,
        max_tokens=1000,
        stream=True,
    )

    return stream

@cl.on_chat_start
def start_chat():
    cl.user_session.set(
        "message_history",
        [{"role": "system", "content": "You are a helpful assistant."}],
    )
    cl.user_session.set("image_history", [{"role": "system", "content": "You are a helpful assistant."}])

@cl.on_message
async def on_message(msg: cl.Message):
    message_history = cl.user_session.get("message_history")
    image_history = cl.user_session.get("image_history")
    
    stream_msg = cl.Message(content="") 
    stream = None

    if msg.elements:
        stream = handle_vision_call(msg, image_history)

    else:
        # add the message in both to keep the coherence between the two histories
        message_history.append({"role": "user", "content": msg.content})
        image_history.append({"role": "user", "content": msg.content})
        
        stream = await gpt_call(message_history)
    
    if stream:
        await process_stream(stream, msg=stream_msg)
        image_history.append({"role": "system", "content": stream_msg.content})
        message_history.append({"role": "system", "content": stream_msg.content})
