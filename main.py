import os
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
import threading
import streamlit.components.v1 as components


config = {
        "toImageButtonOptions": {
            "format": "png",
            "filename": "custom_image",
            "height": 720,
            "width": 480,
            "scale": 6,
        }
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

st.set_page_config(page_title="Volumod.net", page_icon="🔊", layout="wide")


def openTab():
    os.system("streamlit run testing.py")

def callama(prompt):
    response = ollama.chat(
        model='llama3.1:8b',
        messages=[{
            'role': 'user',
            'content': prompt
        }]
    )
    return response['message']['content']

def createCad(prompt,i):
    # Create our client.
    client = Client(token="api-6bf6766f-4756-43cf-adee-3c6007f9ffee")

    # Prompt the API to generate a 3D model from text.
    response = create_text_to_cad.sync(
        client=client,
        output_format=FileExportFormat.STL,
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
        final_result = result.outputs[f"source.stl"]
        with open(f"text-to-cad-output{i}.stl", "w", encoding="utf-8") as output_file:
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


def main(speech, mode):
    # Accesses the speech module
    if mode == "speech":
        speech = speech_to_text()
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
    response = callama(prompt + speech)

    print("***DESIGN SPECIFICATION***")
    st.write("***DESIGN SPECIFICATION***")
    st.write(response)
    print(response)
    print("***END OF DESIGN SPECIFICATION***")
    st.write("***END OF DESIGN SPECIFICATION***")
    prompt = ("Here you are given the detailed idea for a product. Take this idea and make it into a sentance, detailing "
              "all of the measurements for all the parts which would go into making this. Go through the part and specifiy "
              "how large and the shape each part would need to be. Specifiy this in great detail and only respond with the "
              "design measurements and nothing else. When iterating through each apect of the product, state the shape,"
              " size, and all other measurements it has. Finally, describe how to build this Cad model in an iterative way."
              " i.e. I want you to build the product from the base up, iterating each new addition from where it is in relation"
              " to the foundation of the product or another specific part. Do not add in any extra formatting and only "
              "have the response be in a measurement based approach. Here is the design specifcation for the product: ")  + str(response)
    response = callama(prompt)
    st.write("-----------------------------------")
    print("***PRODUCT MEASUREMENTS***")
    st.write("***PRODUCT MEASUREMENTS***")
    st.write(response)
    print(response)
    print("***END OF PRODUCT MEASUREMENTS***")
    st.write("***END OF PRODUCT MEASUREMENTS***")

    prompt = ("Your goal is to take these measurements and seperate them into different parts of the product. You are to"
              " take each part of the assembly and assort them in the following manner. These must be outputted as a list"
              " which looks like the following [Product Part 1: Shape, x length {unit}, x width {unit}...], [Product Part 2: Shape, x length {unit}, x width {unit}...], [...]. DO"
              "NOT FORMAT THE OUTPUT IN ANY OTHER FASHION THAT THE ONE ASKED FOR. DO NOT INCLUDE ANY GREETINGS OR GOODBYES. "
              "ONLY INCLUDE THE ARRAY FORMATTING. Here are the measurements for the product: ")

    response = callama(prompt + str(response))

    st.write("-----------------------------------")
    print("***PARTS LIST***")
    st.write("***PARTS LIST***")
    st.write(response)
    print(response)
    response = list(response.split("\n"))
    print("***END OF PARTS LIST***")
    st.write("***END OF PARTS LIST***")
    st.write("-----------------------------------")
    print("***CAD DESIGN***")
    st.write("***CAD DESIGN***")
    for i in range(len(response)):
        st.write("Designing CAD Part " + str(i+1) + ": " + response[i])
        print("Designing CAD Part " + str(i+1) + ": " + response[i])
        createCad(response[i],i+1)
        print("CAD Part " + str(i+1) + " has been created")
        st.sidebar.write("Cad Part " + str(i+1) + ": /text-to-cad-output" + str(i+1) + ".stl")
    print("***END OF CAD DESIGN***")
    st.write("***END OF CAD DESIGN***")
    # Add in a function call here in the future
    thread1 = threading.Thread(target=openTab)
    thread1.start()


def streamChat():

    st.title("Welcome to Volumod.net")
    components.html(particles_js, height=400, scrolling=False)
    st.sidebar.caption(
        "Built by Aman Kikani. Connect with me on [LinkedIn](https://www.linkedin.com/in/aman-kikani-466716269/)."
    )

    linkedin = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/linkedin.gif"
    topmate = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/topmate.gif"
    email = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/email.gif"
    newsletter = (
        "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/newsletter.gif"
    )
    share = "https://raw.githubusercontent.com/sahirmaharaj/exifa/main/img/share.gif"

    uptime = "https://uptime.betterstack.com/status-badges/v1/monitor/196o6.svg"

    st.sidebar.caption(
        f"""
            <div style='display: flex; align-items: center;'>
                <a href = 'https://www.linkedin.com/in/sahir-maharaj/'><img src='{linkedin}' style='width: 35px; height: 35px; margin-right: 25px;'></a>
                <a href = 'https://topmate.io/sahirmaharaj/362667'><img src='{topmate}' style='width: 32px; height: 32px; margin-right: 25px;'></a>
                <a href = 'mailto:sahir@sahirmaharaj.com'><img src='{email}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
                <a href = 'https://www.linkedin.com/build-relation/newsletter-follow?entityUrn=7163516439096733696'><img src='{newsletter}' style='width: 28px; height: 28px; margin-right: 25px;'></a>
                <a href = 'https://www.kaggle.com/sahirmaharajj'><img src='{share}' style='width: 28px; height: 28px; margin-right: 25px;'></a>

            </div>
            <br>
            <a href = 'https://exifa.betteruptime.com/'><img src='{uptime}'></a>
            &nbsp; <a href="https://www.producthunt.com/posts/exifa-net?embed=true&utm_source=badge-featured&utm_medium=badge&utm_souce=badge-exifa&#0045;net" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=474560&theme=dark" alt="Exifa&#0046;net - Your&#0032;AI&#0032;assistant&#0032;for&#0032;understanding&#0032;EXIF&#0032;data | Product Hunt" style="width: 125px; height: 27px;" width="125" height="27" /></a>

            """,
        unsafe_allow_html=True,
    )
    prompt = st.chat_input("Hello! How can I assist you today?")
    if prompt != None:
        st.write("You: ", prompt)
        main(prompt, 0)

    if st.button("Voice activation mode"):
        main("", "speech")




if __name__ == '__main__':
    streamChat()
