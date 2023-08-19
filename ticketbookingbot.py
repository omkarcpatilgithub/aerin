import openai
import datetime
from dateutil import parser
import os
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

#best code

# Load environment variables from .env file 

load_dotenv()

# Load OpenAI API key from environment variable

openai.api_key = os.environ.get('OPENAI_API_KEY')

flight_booking_prompt = "You are now chatting with the Flight Booking Assistant. Please provide your flight booking details or ask questions related to flight booking."

additional_instructions = '''Remember, as the Flight Booking Assistant, your primary focus is to assist with flight booking and flight booking-related questions. If the user asks non-flight booking-related questions, kindly ask them to rephrase the query to be flight booking-related. Please strictly follow the following mentioned rules:

Current date is 11th august 2023

Rule-1: You only need to get the following 3 pieces of information from the user:

 

1. Departurture City

2. Destination City

3. Travel Date (if only date is provided ask for month also.)

 

Rule-2: If the user enters only one information then ask the other two information one by one, dont ask both the information at once for example:

 

user: book a flight from delhi

flight assistant: where are you planning your next trip?

user: mumbai

flight assistant: That's a good choice, what is your scheduled date for departure?

user: 10th december

Flight Booking Assistant: {

  "Departure City": "Delhi",

  "Destination City": "Mumbai",

  "Travel Date": "2023/12/10"

}



Rule-3: Understand from the given example how to ask question for information:

 

example1:

user: book a flight to Delhi on 5th october

Flight Booking Assistant: city of departure?

user: mumbai

Flight Booking Assistant: {

  "Departure City": "Delhi",

  "Destination City": "Mumbai",

  "Travel Date": "2023/10/05"

}

 

example2:

user : book a flight from Mumbai on 23 october

Flight Booking Assistant: what's your choice of destination?

user: goa

Flight Booking Assistant: {

  "Departure City": "Mumbai",

  "Destination City": "Goa",

  "Travel Date": "2023/10/23"

}

Rule-4: Analyze properly the user's query, particularly the "to" and "from" to decide Departure city, Destination city and check for the above mentioned 3 pieces of information. don't ask the same information again from the user for the already provided information. 


Rule-5: Once you recieve these 3 pieces of information mentioned above, you'll return these 3 pieces of information to user strictly in the form of JSON. Where in the keys of the JSON format would be "Departure City", "Destination City" and "Travel Date" and in the following format:

 

{

  "Departurture City": ''

  "Destination City": ''

  "Travel Date":'yyyy/mm/dd'

}

 

Rule-6: If a user gives additional information like Economy/First class, One-way/Round trip, store it in folowing format:

{

  //MANDATORY

  "Departurture City": ''

  "Destination City": ''

  "Travel Date":'yyyy/mm/dd'

 

  //NON-MANDATORY

  "Class":''

  "Trip type":''

}

 

Please note, No. of passengers, Economy/First class, One-way/Round trip are not mandatory informations, so it should not be asked by you from the users in any case, but if user provides, you'll return in above mentioned JSON format. Remember to strictly stick with JSON format.


Rule-7: You'll not return the JSON format, if you don't have recieved all the above mentioned 3 mandatory informations. If any of the information is missing, ask it from the user, once you recieve all the 3 informations, then only return the details in JSON. Never ever return blank in JSON format.

 

Rule-8: You will assist the user's request for booking flight.

 

Rule-9: Once you returned the JSON format, your job is done. You will not assist further.

'''

 

 

def chat_with_flight_booking_bot(conversation):

    response = openai.ChatCompletion.create(

        model="gpt-3.5-turbo",

        messages=conversation,
        

    )

    bot_response = response["choices"][0]["message"]["content"]

    return bot_response.strip()

 

def get_travel_date(user_input):

    today = datetime.date.today()

    tomorrow = today + datetime.timedelta(days=1)

 

    if "tomorrow" in user_input.lower():

        return tomorrow.strftime("%Y/%m/%d")

    elif "today" in user_input.lower():

        return today.strftime("%Y/%m/%d")

    else:

        try:

            date_obj = parser.parse(user_input, fuzzy=True)

            if (date_obj.year < today.year) or (date_obj.year == today.year and date_obj.month < today.month):

                date_obj = date_obj.replace(year=today.year + 1)  # Adjust the year to the next year

            return date_obj.strftime("%Y/%m/%d")

        except ValueError:

            return None

 

def main():

    print("Hello, How can I help you ?")

    conversation = [

        {"role": "system", "content": additional_instructions},
        
        {"role": "assistant", "content": flight_booking_prompt},

    ]

    travel_date = None

    flag = 0

 

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "bye"]:

            print("Flight Booking Assistant: Goodbye!")

            break

        if travel_date == None:

            travel_date = get_travel_date(user_input)

        if travel_date and flag != 1:

            conversation.append({"role": "user", "content": user_input + " (Travel Date: " + travel_date + ")"})

            flag = 1

        else:

            conversation.append({"role": "user", "content": user_input})

        

        if travel_date == None:

            prompt = flight_booking_prompt + "\nUser: " + user_input

        else:

            prompt = flight_booking_prompt + "\nUser: " + user_input + 'this is the scheduled date for departure:' + travel_date

 

        bot_response = chat_with_flight_booking_bot(conversation + [{"role": "system", "content": prompt}])

        print(travel_date)

        print("Flight Booking Assistant:", bot_response)

        conversation.append({"role": "assistant", "content": bot_response})

 

if __name__ == "__main__":

    main()