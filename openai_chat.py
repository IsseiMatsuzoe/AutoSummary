from openai import OpenAI


def suumarize_text(OPENAI_API_KEY, text):

    client = OpenAI(api_key=OPENAI_API_KEY)

    with open("prompt/first_prompt.txt", "r", encoding="utf-8") as f:
        first_system_prompt = f.read()

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": first_system_prompt},
            {"role": "user", "content": f"次の文章を要約し,markdownで出力せよ:\n{text}"}
        ],
        temperature = 0.7
    )

    markdown_response = response.choices[0].message.content

    with open("prompt/second_prompt.txt", "r", encoding="utf-8") as f:
        second_system_prompt = f.read()

    response = client.chat.completions.create(
        model = "gpt-4o",
        messages=[
            {"role": "system", "content": second_system_prompt},
            {"role": "system", "content": f"Convert markdown input to NOotion API Blocks JSON Array:\n{markdown_response}"}
        ],
        temperature = 0.2
    )
    return response.choices[0].message.content