# !pip install anthropic ipywidgets

import os
import base64
import mimetypes
from anthropic import Anthropic
import ipywidgets as widgets
from IPython.display import display, clear_output, Javascript, HTML 

api_key = os.environ.get("ANTHROPIC_API_KEY", "your-api-key-here")
client = Anthropic(api_key=api_key)
conversation_history = []

output_area = widgets.Output(
    layout={'border': '1px solid black', 'height': '400px', 'overflow_y': 'auto', 'width': '100%'}
)
text_input = widgets.Text(
    placeholder='Type your message here (or paste an image/file)...', 
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
# Create a status HTML widget with a specific ID
paste_status = widgets.HTML(
    value="<div id='paste-status-indicator'><i>Tip: You can paste images or files directly into the message box</i></div>",
    layout=widgets.Layout(width='50%')
)

# Variable to store paste data
pasted_file = None

def encode_file(file_data, mime_type):
    file_b64 = base64.b64encode(file_data).decode('utf-8')
    
    return {
        "type": "image" if mime_type.startswith("image/") else "file",
        "source": {
            "type": "base64",
            "media_type": mime_type,
            "data": file_b64
        }
    }

# Improved JavaScript to handle paste events - more reliable selector
paste_js = """
// Wait for the DOM to be fully loaded
setTimeout(function() {
    // Add paste event listener to the document
    document.addEventListener('paste', function(e) {
        var items = (e.clipboardData || e.originalEvent.clipboardData).items;
        
        for (var i = 0; i < items.length; i++) {
            if (items[i].kind === 'file') {
                var blob = items[i].getAsFile();
                var reader = new FileReader();
                
                reader.onload = function(event) {
                    // Get base64 data without the prefix
                    var base64data = event.target.result;
                    var mimeType = blob.type;
                    var fileName = "pasted_" + new Date().getTime() + "." + mimeType.split('/')[1];
                    
                    // Pass the data to Python
                    IPython.notebook.kernel.execute(
                        "pasted_file = {'data': '" + base64data + "', 'mime_type': '" + 
                        mimeType + "', 'name': '" + fileName + "'}"
                    );
                    
                    // Find our status element by ID and update it
                    var statusElement = document.getElementById('paste-status-indicator');
                    if (statusElement) {
                        statusElement.innerHTML = "<b style='color:green'>✓ File pasted: " + fileName + "</b>";
                    }
                };
                
                reader.readAsDataURL(blob);
                e.preventDefault();
                break;
            }
        }
    });
}, 1000);  // Wait 1 second for elements to be properly rendered
"""

# Create a file upload widget as a backup option
file_upload = widgets.FileUpload(
    description='Or upload:',
    accept='',
    multiple=False,
    layout=widgets.Layout(width='50%')
)

input_row = widgets.HBox([text_input, send_button], layout=widgets.Layout(width='100%'))
status_row = widgets.HBox([paste_status, file_upload], layout=widgets.Layout(width='100%'))
controls_row = widgets.HBox([model_dropdown, max_tokens_slider, clear_button], layout=widgets.Layout(width='100%'))
interface = widgets.VBox([
    output_area, 
    input_row,
    status_row,
    controls_row
], layout=widgets.Layout(width='900px'))

def send_message(sender):
    global conversation_history, pasted_file
    user_message = text_input.value
    
    # Check for file from either paste or upload
    has_file = pasted_file is not None or len(file_upload.value) > 0
    
    if not user_message.strip() and not has_file:
        return
    
    text_input.value = ''
    
    with output_area:
        file_content = None
        file_name = None
        
        # Process pasted file
        if pasted_file:
            try:
                file_name = pasted_file['name']
                print(f"You: [Pasted file: {file_name}]")
                if user_message:
                    print(f"You: {user_message}")
                
                # Process the base64 data
                # Remove the prefix (e.g., "data:image/png;base64,")
                base64_data = pasted_file['data'].split(',', 1)[1]
                
                file_content = {
                    "type": "image" if pasted_file['mime_type'].startswith("image/") else "file",
                    "source": {
                        "type": "base64",
                        "media_type": pasted_file['mime_type'],
                        "data": base64_data
                    }
                }
                
                # Reset pasted file
                pasted_file = None
                paste_status.value = "<div id='paste-status-indicator'><i>Tip: You can paste images or files directly into the message box</i></div>"
                
            except Exception as e:
                print(f"Error processing pasted file: {str(e)}")
        
        # Process uploaded file (if no pasted file)
        elif file_upload.value:
            try:
                file_data = list(file_upload.value.items())[0][1]
                file_name = file_data['name']
                print(f"You: [Uploaded file: {file_name}]")
                if user_message:
                    print(f"You: {user_message}")
                
                file_bytes = file_data['content']
                file_b64 = base64.b64encode(file_bytes).decode('utf-8')
                content_type = file_data.get('type', 'application/octet-stream')
                
                file_content = {
                    "type": "image" if content_type.startswith("image/") else "file",
                    "source": {
                        "type": "base64",
                        "media_type": content_type,
                        "data": file_b64
                    }
                }
                
                # Clear upload widget
                file_upload.value = {}
                
            except Exception as e:
                print(f"Error processing uploaded file: {str(e)}")
        
        # Text only message
        else:
            print(f"You: {user_message}")
        
        # Create message content
        if file_content and user_message:
            message_content = [
                file_content,
                {"type": "text", "text": user_message}
            ]
        elif file_content:
            message_content = [file_content]
        else:
            message_content = user_message
            
        # Add to conversation history
        conversation_history.append({
            "role": "user", 
            "content": message_content
        })
        
        try:
            print("Claude is thinking...", end="")
            
            response = client.messages.create(
                model=model_dropdown.value,
                max_tokens=max_tokens_slider.value,
                messages=conversation_history
            )
            
            claude_response = response.content[0].text
            
            clear_output(wait=True)
            
            # Re-display user message
            if file_name and user_message:
                print(f"You: [File: {file_name}]")
                print(f"You: {user_message}")
            elif file_name:
                print(f"You: [File: {file_name}]")
            else:
                print(f"You: {user_message}")
            
            print(f"Claude: {claude_response}")
            
            conversation_history.append({"role": "assistant", "content": claude_response})
            
        except Exception as e:
            clear_output(wait=True)
            if file_name:
                print(f"You: [File: {file_name}]")
            if user_message:
                print(f"You: {user_message}")
            print(f"Error: {str(e)}")

def clear_chat(sender):
    global conversation_history, pasted_file
    conversation_history = []
    pasted_file = None
    file_upload.value = {}
    paste_status.value = "<div id='paste-status-indicator'><i>Tip: You can paste images or files directly into the message box</i></div>"
    with output_area:
        clear_output()
        print("Chat history cleared.")

send_button.on_click(send_message)
clear_button.on_click(clear_chat)
text_input.on_submit(lambda w: send_message(None))

display(interface)

# Display the JavaScript to enable paste functionality
display(Javascript(paste_js))

with output_area:
    print("Welcome to Claude Chat! Type a message or paste an image/file to begin.")
