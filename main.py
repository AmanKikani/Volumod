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
