
# This is an automated programming documentation scraper for usage in replit AI context
# It uses free APIs therefore implies many limitations such as groq context length
# The scraped content quality can be improved with paid AI services
#
# Created by Vertinski
# (oc) 2024



### module installation ###
import subprocess
import sys

required_modules = ["duckduckgo-search", "groq"]

for module in required_modules:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", module])



from duckduckgo_search import DDGS
from groq import Groq
import requests
import os



### groq functions ###
# get search result text body by matching link from dict 
def content_by_href(results, target_href):
    for result in results:
        if result['href'] == target_href:
            return result['body']
    return None


def groq_chat (programming_language, user_question, search_results): 
    rezultz = " ".join([str(value) for item in search_results for value in item.values()])

    # the api key expires after some time period
    groq_api_key = os.environ['GROQ_API_KEY']
    client = Groq (api_key=groq_api_key,)

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a smart AI assistant giving concise answers."
            },
            {
                "role": "user",
                "content": f"programming language: {programming_language} \nuser question: {user_question} \n\nsearch results: {rezultz} \n\ntask: which resource is pointing to the most recent version of documentation answering the user question? give one most relevant link! write the correct url without any other explanations."
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=100,
        temperature=0.14
    )

    web_url = chat_completion.choices[0].message.content

    page_intro = content_by_href(search_results, web_url)
    #print ("page intro: ", page_intro)
    #input ("debug......")

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a smart AI assistant giving concise answers."
            },
            {
                "role": "user",
                "content": f"if this site content: \n'{page_intro}' \nis appropriate for {programming_language} language write 'True', otherwise write 'Language mismatch'",
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=100,
        temperature=0.14
    )

    result = chat_completion.choices[0].message.content
    print (f"\nresult: {result}")
    if result == "True":
        return web_url
    else:
        return "Language mismatch"


# Result cleanup will be available when groq allows larger limits for paid users
def clean_result(search_result, programming_language):
    # Initialize Groq client
    groq_api_key = os.environ['GROQ_API_KEY']
    client = Groq(api_key=groq_api_key)

    # Create the prompt for Groq
    prompt = f"""
    Given the following search result for {programming_language} documentation:

    {search_result}

    Task: Remove unnecessary links, leftover menu items, and other preceding content which is not relevant to the code documentation part.
    Return only the block of relevant documentation content, including caption.
    Important: Do not modify or summarize the relevant content - return it verbatim!
    """

    # Make the API call to Groq
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a precise content extractor. Extract only the relevant documentation, removing all unnecessary elements."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="llama-3.1-70b-versatile",
        max_tokens=8000,
        temperature=0.05
    )

    # Extract and return the cleaned content
    cleaned_content = chat_completion.choices[0].message.content
    return cleaned_content


### jina functions ###
def web_request(url: str):
    full_url = 'https://r.jina.ai/' + url
    
    try:
        response = requests.get(full_url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        
        # Return the response content
        return response.text

    except requests.exceptions.RequestException as e:
        # Handle any type of request exception
        raise RuntimeError(f"An error occurred while fetching the URL: {str(e)}")




def main():
    #create empty file for storing the documentation data
    if not os.path.exists('docs'):
        os.makedirs('docs')
    with open('docs/documentation.txt', 'w') as f:
        f.write("")

    print ("\n\n\n")
    print ("       _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _")
    print ("  -=≡|| RepliDocs by Vertinski (oc) 2024 ||≡=-")
    print ("       ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯")
    print ("   Type 'exit' to quit, 'help' for explanation.\n\n")

    print ("¡Add '/docs/documentation.txt' file to Your IDE's AI context to start!\n")

    user_input = False
    while not user_input:
        user_input = input ("Set Your programming language: ")
    print()
    programming_language = user_input.lower()
    
    while True:
        # Get input directly from the user
        user_input = input(f"[{programming_language}] Search RepliDocs: ")

        # ignore empty inputs
        if not user_input.strip():
            continue
        
        elif user_input.lower() == 'exit':
            print("Exiting the program. Goodbye!\n")
            break

        elif user_input.lower().startswith('lang'):
            _, new_language = user_input.split(maxsplit=1)
            programming_language = new_language.lower()
            print(f"Programming language set to: {programming_language}\n")

        elif user_input.lower().startswith('buff'):
            print("buff not yet implemented...")

        elif user_input.lower().startswith('clear'):
            with open('docs/documentation.txt', 'w') as f:
                f.write("")
            
        elif user_input.lower() == 'help':
            print("\nAvailable commands:")
            print("'lang':  Change Your programming language")
            print("'buff <int>':  Set the document count in the buffer")
            print("'clear': Clear the 'documentation.txt' file to free AI context space")
            print("'exit':  Quit the program")
            print("'help':  Show this help message")
            print("\nNote: Replit allows very small AI context size - so the 'documentation.txt' file \nis limited to 21k characters or 5,200 tokens. Otherwise Replit removes \nother project files from AI context, which of course sucks. Thus the buffer \ncontains only the most recent search result. Keep that in mind when \ntalking to AI.")
            print()
        
        else:
            results = DDGS().text(f"{programming_language}, {user_input}", max_results=6)
            
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    source = groq_chat(programming_language, user_input, results)
                    break
                except Exception as e:
                    if attempt < max_retries:
                        print("Groq failed to get the source or is not responding \nTrying again...\n")
                    else:
                        print(f"Groq failed to get source: {str(e)}")

            if source == "Language mismatch":
                print ("Language mismatch in search results. Please try again!\n")

            else:
                try:
                    result = web_request (source)
                    #print (result)
                    #input ("debug......")
                    
                    response_text = result#["content"]  # Extract the response text
                    #response_text = clean_result (response_text, programming_language)  #filter the scraped result with groq (when available))
                    
                    with open('docs/documentation.txt', 'w') as f:
                        f.write(response_text[-21000:])  #hard crop the text :(
                        
                    print(f"Documentation added to AI context! \nSource: {source}")
        
                except RuntimeError as e:
                    print(e)
                    
                #print(repr(user_input))  # repr() shows the exact representation of the string
                print()  # Print a blank line for better readability


if __name__ == "__main__":
    main()

