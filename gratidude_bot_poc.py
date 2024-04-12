from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
  # model="gpt-3.5-turbo", 
  model="gpt-4-1106-preview",
  # messages=[
  #   {"role": "system", "content": "You are a conversational assistant that helps people express and share gratitude. You are friendly, calm, and supportive."},
  #   {"role": "user", "content": "Someone has recently logged the following in their gratitude journal. Summarize the entries for them in under 160 characters. Look for themes or people of interest. Make a recommendation based on the entries. You are trying to encourage a daily practice of gratitude. \
  #   01/01/2024: Danielle.\
  #   01/02/2024: my health.\
  #   01/03/2024: my husband.\
  #   01/09/2024: my job.\
  #   01/11/2024: my children.\
  #   01/12/2024: Danielle.\
  #   01/22/2024: my health.\
  #   01/23/2024: my home."}
  # ]
  messages=[
    {"role": "system", "content": "You are a conversational assistant that helps people express and share gratitude. You are friendly, calm, and supportive."},
    {"role": "user", "content": "Someone has recently logged the following in their gratitude journal. In under 160 characters, ask them a followup question related to the entry in order to add impact and vibrancy to the memory. \
    Entry: I'm grateful for my friend Alissa"}
  ]
)

print(completion.choices[0].message)
