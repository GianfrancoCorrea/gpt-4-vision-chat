# Welcome to GPT 4 turbo vision! 🚀🤖

## Upload an image 🔗
Drag & Drop, or click in the "UPLOAD FILES" button, on the left of the chat input 💬

### GPT-4-1106-preview for messages that ARE NOT images 📝
* change log:
    - Changed GPT-4-1106-preview for gpt-3.5-turbo-1106, due high cost of GPT-4-1106-preview
### gpt-4-vision-preview for messages that ARE images 📷
If you upload more than 1 image, it will take the first image, this is just for demo purposes
* change log:
    - Change max_tokens from the output to 300


## install dependencies (recomended to use a [virtualenv](https://docs.python.org/3/library/venv.html))
```bash
pip install -r requirements.txt
```

## add the api key to the environment (.env)
```bash
OPENAI_API_KEY=<your api key>
```

## run the app
```bash
chainlit run app.py
```

## run the app with a specific port
```bash
chainlit run app.py --port 5001
```
