import ollama
import speech_recognition as sr
import time
import streamlit as st
from kittycad.api.ml import create_text_to_cad, get_text_to_cad_model_for_user
from kittycad.client import Client
from kittycad.models import (
    ApiCallStatus,
    Error,
    FileExportFormat,
    TextToCad,
    TextToCadCreateBody,
)
import pandas as pd
import random

config = {
    "toImageButtonOptions": {
        "format": "png",
        "filename": "custom_image",
        "height": 720,
        "width": 480,
        "scale": 6,
    }
}

icons = {
    "assistant": "https://raw.githubusercontent.com/sahirmaharaj/exifa/2f685de7dffb583f2b2a89cb8ee8bc27bf5b1a40/img/assistant-done.svg",
    "user": "https://raw.githubusercontent.com/sahirmaharaj/exifa/2f685de7dffb583f2b2a89cb8ee8bc27bf5b1a40/img/user-done.svg",
}

particles_js = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Particles.js</title>
  <style>
  #particles-js {
    position: fixed;
    width: 100vw;
    height: 100vh;
    top: 0;
    left: 0;
    z-index: -1; /* Send the animation to the back */
  }
  .content {
    position: relative;
    z-index: 1;
    color: white;
  }

</style>
</head>
<body>
  <div id="particles-js"></div>
  <div class="content">
    <!-- Placeholder for Streamlit content -->
  </div>
  <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
  <script>
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 300,
          "density": {
            "enable": true,
            "value_area": 800
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          },
          "polygon": {
            "nb_sides": 5
          },
          "image": {
            "src": "img/github.svg",
            "width": 100,
            "height": 100
          }
        },
        "opacity": {
          "value": 0.5,
          "random": false,
          "anim": {
            "enable": false,
            "speed": 1,
            "opacity_min": 0.2,
            "sync": false
          }
        },
        "size": {
          "value": 2,
          "random": true,
          "anim": {
            "enable": false,
            "speed": 40,
            "size_min": 0.1,
            "sync": false
          }
        },
        "line_linked": {
          "enable": true,
          "distance": 100,
          "color": "#ffffff",
          "opacity": 0.22,
          "width": 1
        },
        "move": {
          "enable": true,
          "speed": 0.2,
          "direction": "none",
          "random": false,
          "straight": false,
          "out_mode": "out",
          "bounce": true,
          "attract": {
            "enable": false,
            "rotateX": 600,
            "rotateY": 1200
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": true,
            "mode": "grab"
          },
          "onclick": {
            "enable": true,
            "mode": "repulse"
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 1
            }
          },
          "bubble": {
            "distance": 400,
            "size": 2,
            "duration": 2,
            "opacity": 0.5,
            "speed": 1
          },
          "repulse": {
            "distance": 200,
            "duration": 0.4
          },
          "push": {
            "particles_nb": 2
          },
          "remove": {
            "particles_nb": 3
          }
        }
      },
      "retina_detect": true
    });
  </script>
</body>
</html>
"""

st.set_page_config(page_title="Exifa.net", page_icon="✨", layout="wide")

welcome_messages = [
    "Hello! I'm Exifa, an AI assistant designed to make image metadata meaningful. Ask me anything!",
    "Hi! I'm Exifa, an AI-powered assistant for extracting and explaining EXIF data. How can I help you today?",
    "Hey! I'm Exifa, your AI-powered guide to understanding the metadata in your images. What would you like to explore?",
    "Hi there! I'm Exifa, an AI-powered tool built to help you make sense of your image metadata. How can I help you today?",
    "Hello! I'm Exifa, an AI-driven tool designed to help you understand your images' metadata. What can I do for you?",
    "Hi! I'm Exifa, an AI-driven assistant designed to make EXIF data easy to understand. How can I help you today?",
    "Welcome! I'm Exifa, an intelligent AI-powered tool for extracting and explaining EXIF data. How can I assist you today?",
    "Hello! I'm Exifa, your AI-powered guide for understanding image metadata. Ask me anything!",
    "Hi! I'm Exifa, an intelligent AI assistant ready to help you understand your images' metadata. What would you like to explore?",
    "Hey! I'm Exifa, an AI assistant for extracting and explaining EXIF data. How can I help you today?",
]

message = random.choice(welcome_messages)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": message}]
if "exif_df" not in st.session_state:
    st.session_state["exif_df"] = pd.DataFrame()
if "url_exif_df" not in st.session_state:
    st.session_state["url_exif_df"] = pd.DataFrame()
if "show_expanders" not in st.session_state:
    st.session_state.show_expanders = True
if "reset_trigger" not in st.session_state:
    st.session_state.reset_trigger = False
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = None
if "image_url" not in st.session_state:
    st.session_state["image_url"] = ""
if "follow_up" not in st.session_state:
    st.session_state.follow_up = False
if "show_animation" not in st.session_state:
    st.session_state.show_animation = True


def createCad(prompt,i):
    # Create our client.
    client = Client(token="api-6bf6766f-4756-43cf-adee-3c6007f9ffee")

    # Prompt the API to generate a 3D model from text.
    response = create_text_to_cad.sync(
        client=client,
        output_format=FileExportFormat.STEP,
        body=TextToCadCreateBody(
            prompt=prompt,
        ),
    )

    if isinstance(response, Error) or response is None:
        print(f"Error: {response}")
        exit(1)

    result: TextToCad = response

    # Polling to check if the task is complete
    while result.completed_at is None:
        # Wait for 5 seconds before checking again
        time.sleep(5)

        # Check the status of the task
        response = get_text_to_cad_model_for_user.sync(
            client=client,
            id=result.id,
        )

        if isinstance(response, Error) or response is None:
            print(f"Error: {response}")
            exit(1)

        result = response

    if result.status == ApiCallStatus.FAILED:
        # Print out the error message
        print(f"Text-to-CAD failed: {result.error}")

    elif result.status == ApiCallStatus.COMPLETED:
        if result.outputs is None:
            print("Text-to-CAD completed but returned no files.")
            exit(0)

        # Print out the names of the generated files
        print(f"Text-to-CAD completed and returned {len(result.outputs)} files:")
        for name in result.outputs:
            print(f"  * {name}")

        # Save the STEP data as text-to-cad-output.step
        final_result = result.outputs[f"source{i}.step"]
        with open("text-to-cad-output.step", "w", encoding="utf-8") as output_file:
            output_file.write(final_result.decode("utf-8"))
            print(f"Saved output to {output_file.name}")


def speech_to_text():
    # Creates the recognizer and turns the outptut into text
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Speak now...")
        audio_data = recognizer.listen(source)
    # Makes sure the audio is recognized and there are no errors
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"


def main():
    # Accesses the speech module
    # speech = speech_to_text()
    speech = "Bottle opener"
    print(speech)

    # Engineering prompt
    prompt = ("You are working as a Cad Designer using the Text To Cad functionality. Here you are given a conversation"
              " detailing what a customer wants out of a product. Your goal as an expert cad designer is to respond with"
              "the expected dimensions of the product and all of the things it would need to function. This means that "
              "if the user wants a product to be made, what you need to do is come up with the measurements and specifications"
              " that will go into a text to cad software which will then generate the product. Please respond with only the "
              " product measurements and specifications. Here is the folowing conversation. YOU MUST ONLY RESPOND WITH"
              " THE PRODUCT MEASUREMENTS, NO OTHER THINGS IN THE RESPONSE BESIDES THE MEASUREMENTS. DETAIL THE MEASUREMENTS"
              " OF EACH ASPECT OF THE PART ONLY: ")

    # Calls the local ollama chatbot
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[{
            'role': 'user',
            # Appends the engineering prompt to the speech
            'content':  prompt + speech
        }]
    )
    print("***DESIGN SPECIFICATION***")
    st.write(response['message']['content'])
    print(response['message']['content'])
    print("***END OF DESIGN SPECIFICATION***")
    prompt = ("Here you are given the detailed idea for a product. Take this idea and make it into a sentance, detailing "
              "all of the measurements for all the parts which would go into making this. Go through the part and specifiy "
              "how large and the shape each part would need to be. Specifiy this in great detail and only respond with the "
              "design measurements and nothing else. When iterating through each apect of the product, state the shape,"
              " size, and all other measurements it has. Finally, describe how to build this Cad model in an iterative way."
              " i.e. I want you to build the product from the base up, iterating each new addition from where it is in relation"
              " to the foundation of the product or another specific part. Do not add in any extra formatting and only "
              "have the response be in a measurement based approach. Here is the design specifcation for the product: ")  + str(response['message']['content'])
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    print("***PRODUCT MEASUREMENTS***")
    st.write(response['message']['content'])
    print(response['message']['content'])
    print("***END OF PRODUCT MEASUREMENTS***")

    prompt = ("Your goal is to take these measurements and seperate them into different parts of the product. You are to"
              " take each part of the assembly and assort them in the following manner. These must be outputted as a list"
              " which looks like the following [Product Part 1: Shape, x length {unit}, x width {unit}...], [Product Part 2: Shape, x length {unit}, x width {unit}...], [...]. DO"
              "NOT FORMAT THE OUTPUT IN ANY OTHER FASHION THAT THE ONE ASKED FOR. DO NOT INCLUDE ANY GREETINGS OR GOODBYES. "
              "ONLY INCLUDE THE ARRAY FORMATTING. Here are the measurements for the product: ")

    response = ollama.chat(
        model='llama3.1:8b',
        messages=[{
            'role': 'user',
            'content': prompt + str(response['message']['content'])
        }]
    )
    print("***PARTS LIST***")
    st.write(response['message']['content'])
    print(response['message']['content'])
    response = list(response['message']['content'].split("\n"))
    print("***END OF PARTS LIST***")

    print("***CAD DESIGN***")
    for i in range(len(response)):
        st.write("Designing CAD Part " + str(i+1) + ": " + response[i])
        print("Designing CAD Part " + str(i+1) + ": " + response[i])
    print("***END OF CAD DESIGN***")

def streamChat():
    st.title("Conversation CAD builder")
    if st.button("Start"):
        main()

if __name__ == '__main__':
    streamChat()
