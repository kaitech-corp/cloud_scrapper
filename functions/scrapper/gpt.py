import openai
from google_secrets import get_secret


class GPT:
    def generate_tags(self, content):

        openai.api_key = get_secret('openAI_api_key')

        model = "gpt-3.5-turbo-16k-0613"
        role = "Cloud Computing Expert"
        prompt = "Generate 10 tags from the following text data and provide the tags in a list format: " + content
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": prompt}
                ]
            )
            if response and response.choices:
                tags = response.choices[0].message.content
                return tags
            else:
                # Handle the case where the response is empty or doesn't contain choices
                return "Error: Empty response from GPT-3.5-turbo"
        except Exception as e:
            # Handle any exceptions that may occur during the API call
            return f"Error: {str(e)}"
        
    def generate_summary(self, content):

        openai.api_key = get_secret('openAI_api_key')

        model = "gpt-3.5-turbo-16k-0613"
        role = "Cloud Computing Expert"
        prompt = "Generate a detailed report and add definitions and explainations where necessary to explain the following content: " + content
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {"role": "system", "content": role},
                    {"role": "user", "content": prompt}
                ]
            )
            if response and response.choices:
                summary = response.choices[0].message.content
                return summary
            else:
                # Handle the case where the response is empty or doesn't contain choices
                return "Error: Empty response from GPT-3.5-turbo"
        except Exception as e:
            # Handle any exceptions that may occur during the API call
            return f"Error: {str(e)}"