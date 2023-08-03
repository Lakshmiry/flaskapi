
import openai
from flask import Flask, request, jsonify 
from flask_cors import CORS 
 
app = Flask(__name__) 
CORS(app) 
 
file_path = "secret.txt" 
with open(file_path, "r") as file: 
    file_contents = file.read() 
 
openai.api_key = file_contents 

basic_prompts = ["hi", "hello", "thankyou"] 


def updateList(message : str, pl: list[str]):
  pl.append(message)

def create_prompt(message : str, pl: list[str]) -> str:
  p_message : str = f'\nHuman: {message}'
  updateList(p_message,pl)
  prompt : str = ''.join(pl)
  return  prompt

def get_bot_response(message : str, pl: list[str]) -> str:
  prompt: str = create_prompt(message,pl)
  bot_response : str = get_davinci_api_response(prompt)

  if bot_response:
    updateList(bot_response,pl)
    pos : int = bot_response.find('\nAI: ')
    bot_response = bot_response[pos +5:]
  else:
    bot_response = "Something Went Wrong"

  return bot_response


def check_model(user_input):

    if user_input.lower() in basic_prompts:
    
        prompt_list: list[str] = [f'Detect the disease and symptoms from trained dataset and return the diagnosis code only. if propmpt not available in dataset then specify "No such disease found". if prompt is hello, hi etc, then reply with simple greeting message ',
                                '\nHuman: typhoid fever',
                                '\nAI: Diagnosis code for typhoid fever is 0020']

        response = get_bot_response(user_input, prompt_list)
 
    else:

        response= get_api_response(user_input + " ###")

    return response


def get_api_response(message):  
     
    try:  
        response: dict = openai.Completion.create(  
             model = "davinci:ft-personal:medicalmodel-2023-07-27-03-20-26",
            prompt= message,  
            temperature=0,  
            max_tokens=150,  
            top_p=1,  
            frequency_penalty=0,  
            presence_penalty=0.6,  
            stop=['END']  
        )  
        choices: dict = response.get('choices')[0]  
        text = choices.get('text')  
  
    except Exception as e:  
        print("Error", e)  
  
    return text  


def get_davinci_api_response(prompt : str) -> str | None:
  text : str | None = None
  try:
      response : dict = openai.Completion.create(
        model = "text-davinci-003",
        prompt = prompt,
        temperature = 0.9,
        max_tokens= 150,
        top_p =1,
        frequency_penalty=0,
        presence_penalty = 0.6,
        stop =[ ' Human:', ' AI:']
      )
      choices : dict = response.get('choices')[0]
      text = choices.get('text')
  except Exception as e:
    print("Error",e)

  return text



  
@app.route('/chat', methods=['POST'])  
def chat():  
    data = request.get_json()  
    user_input = data['user_input']  
    response = check_model(user_input);  
    return jsonify({'response': response})  
 
 
if __name__ == '__main__': 
    app.run(debug=True)
