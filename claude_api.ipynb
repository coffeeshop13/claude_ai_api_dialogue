# !pip install anthropic ipywidgets

import os
import base64
import mimetypes
from anthropic import Anthropic
import ipywidgets as widgets
from IPython.display import display, clear_output

api_key = os.environ.get("ANTHROPIC_API_KEY", "your-api-key")
client = Anthropic(api_key=api_key)
conversation_history = []

output_area = widgets.Output(
    layout={'border': '1px solid black', 'height': '400px', 'overflow_y': 'auto', 'width': '100%'}
)
text_input = widgets.Text(
    placeholder='Type your message here...', 
    layout=widgets.Layout(width='90%')
)
send_button = widgets.Button(
    description='Send', 
    button_style='primary',
    layout=widgets.Layout(width='10%')
)
clear_button = widgets.Button(
    description='Clear Chat', 
    button_style='danger'
)
model_dropdown = widgets.Dropdown(
    options=['claude-3-5-sonnet-20240620', 'claude-3-opus-20240229', 'claude-3-5-haiku-20240307', 'claude-3-7-sonnet-20250219'],
    value='claude-3-7-sonnet-20250219',
    description='Model:',
)
max_tokens_slider = widgets.IntSlider(
    value=1000,
    min=100,
    max=4000,
    step=100,
    description='Max Tokens:',
    disabled=False
)
file_upload = widgets.FileUpload(
    description='Upload File:',
    accept='',
    multiple=False,
    layout=widgets.Layout(width='50%')
)

def encode_file(file_data):
    content_type = file_data.get('type', 'application/octet-stream')
    if not content_type or content_type == 'application/octet-stream':
        content_type, _ = mimetypes.guess_type(file_data['name'])
        if not content_type:
            content_type = 'application/octet-stream'
    
    file_bytes = file_data['content']
    file_b64 = base64.b64encode(file_bytes).decode('utf-8')
    
    return {
        "type": "image" if content_type.startswith("image/") else "file",
        "source": {
            "type": "base64",
            "media_type": content_type,
            "data": file_b64
        }
    }

input_row = widgets.HBox([text_input, send_button], layout=widgets.Layout(width='100%'))
file_row = widgets.HBox([file_upload], layout=widgets.Layout(width='100%'))
controls_row = widgets.HBox([model_dropdown, max_tokens_slider, clear_button], layout=widgets.Layout(width='100%'))
interface = widgets.VBox([
    output_area, 
    input_row, 
    file_row,
    controls_row
], layout=widgets.Layout(width='900px'))

def send_message(sender):
    global conversation_history
    user_message = text_input.value
    
    if not user_message.strip() and not file_upload.value:
        return
    
    text_input.value = ''
    
    with output_area:
        file_content = None
        if file_upload.value:
            file_data = list(file_upload.value.items())[0][1]
            try:
                file_name = file_data['name']
                print(f"You: [Uploaded file: {file_name}]")
                if user_message:
                    print(f"You: {user_message}")
                
                file_content = encode_file(file_data)
                
                if user_message:
                    message_content = [
                        file_content,
                        {"type": "text", "text": user_message}
                    ]
                else:
                    message_content = [file_content]
                
                conversation_history.append({
                    "role": "user", 
                    "content": message_content
                })
                
                file_upload.value = {}
                
            except Exception as e:
                print(f"Error processing file: {str(e)}")
                if user_message:
                    print(f"You: {user_message}")
                    conversation_history.append({"role": "user", "content": user_message})
        else:
            print(f"You: {user_message}")
            conversation_history.append({"role": "user", "content": user_message})
        
        try:
            print("Claude is thinking...", end="")
            
            response = client.messages.create(
                model=model_dropdown.value,
                max_tokens=max_tokens_slider.value,
                messages=conversation_history
            )
            
            claude_response = response.content[0].text
            
            clear_output(wait=True)
            
            if file_content and user_message:
                print(f"You: [Uploaded file: {file_data['name']}]")
                print(f"You: {user_message}")
            elif file_content:
                print(f"You: [Uploaded file: {file_data['name']}]")
            else:
                print(f"You: {user_message}")
            
            print(f"Claude: {claude_response}")
            
            conversation_history.append({"role": "assistant", "content": claude_response})
            
        except Exception as e:
            clear_output(wait=True)
            print(f"You: {user_message}")
            print(f"Error: {str(e)}")

def clear_chat(sender):
    global conversation_history
    conversation_history = []
    file_upload.value = {}
    with output_area:
        clear_output()
        print("Chat history cleared.")

send_button.on_click(send_message)
clear_button.on_click(clear_chat)
text_input.on_submit(lambda w: send_message(None))

display(interface)

with output_area:
    print("Welcome to Claude Chat! Type a message or upload a file to begin.")
