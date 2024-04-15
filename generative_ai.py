from openai import OpenAI
client = OpenAI()

def generate_response(gratitude_submission):
  completion = client.chat.completions.create(
    model="gpt-4-1106-preview",

    messages=[
      {"role": "system", "content": "You are a conversational assistant that helps people express and share gratitude. You are smart, calm, supportive, and sometimes clever."},
      {"role": "user", "content": "Someone has recently logged the following in their gratitude journal. In under 160 characters, ask them an interesting followup question related to the entry in order to add vibrancy to the memory. Use emojis in your responses sometimes to add color.\
      Entry:"+gratitude_submission}
    ]
  )
  print(completion.choices[0].message)
  return completion.choices[0].message