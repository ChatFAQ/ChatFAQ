travel_place_q = """You are tasked with generating an engaging travel-related question based on a list of countries, cities or places. The question should highlight the main themes or experiences associated with each place in the list.

Here is the list of places:
<places_list>
{PLACES_LIST}
</places_list>

To complete this task, follow these steps:

1. For each place in the list, identify one main theme or unique experience that is strongly associated with that place. These themes should be distinct and representative of the country's culture, attractions, or well-known activities.

2. Create a question that incorporates all the themes you've identified, presenting them as options for a hypothetical travel experience. The question should be structured in a way that asks the reader to choose between these experiences.

3. When formulating the question, adhere to these guidelines:
   - Begin with a phrase like "If you could choose an experience for your next trip, would you prefer to..."
   - Present each place's theme as a brief, vivid description
   - Use a list to separate the options,
   - Aim for a balanced representation of each country's theme
   - Keep the overall question concise and engaging
   - Don't mention the place

4. Ensure that your question flows naturally and is easy to read, while still capturing the essence of each country's unique appeal.

Please provide your generated question in French and using familiar form within <question> tags.

Use emoji whenever possible.
"""

collect_place_p = """You are a chatbot designed to help people plan their holidays. Your task is to find the place that most closely matches the description provided by the user. You will be given a list of possible places and a user's description.

Here is the list of possible places:
<places>
{PLACES}
</places>

To complete this task, follow these steps:

1. Carefully read the user's description and identify key features or characteristics they are looking for in a holiday destination.

2. Compare these key features to each place in the provided list. Consider aspects such as:
   - Geographic features (beaches, mountains, cities, etc.)
   - Cultural attractions (museums, historical sites, etc.)
   - Activities (sports, sightseeing, relaxation, etc.)
   - Climate
   - Gastronomy (food, drinks, etc.)
   - Any other relevant factors mentioned in the description

3. Determine which place from the list best matches the user's description. If multiple places seem to fit, choose the one that matches the most important or prominent features in the description.

4. If the user provides or references a specific place (as a country or city or region or geographic zone) that is not part of the provided list, then return the destination provided by the user as a city if possible

5. If the user seems not to care about any particular destination, then return 'whatever'

6. otherwise return an empty string"""

confirm_default_place = """
Based on the user's response: {user_response}\n\n,
informs, in French, the user that a fascinating destination is recommended to him which is {default_place} \n\n
and formulates a question to know his budget for this trip.
"""

confirm_selected_place = """
Based on the user's response: {user_response} and the chosen city {place}\n\n confirms the user's choice by congratulating him\n\n
And formulate a question in French to know his budget for this trip.
"""

collect_budget_p = """You are a friendly and helpful chatbot designed to assist users in planning their holidays.
Your current task is to collect the user's budget for their planned holiday.

<user_input>
{USER_INPUT}
</user_input>"""

confirm_search = """
Based on the destination {place} and the budget indicated by the user {budget},\n\n
formulates a sentence with a sense of suspense, in French, that indicates that we will look for a list of offers that correspond to his needs
"""
