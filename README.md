# Kwork_parse 
This is the parser of kwork.ru. 

This script process cards of freelance marketplace by the AI(Mistral, Gigachat).
Target of this script - get analyzed test task and print required skills, stack and short description.

## Login
Before authorization, you need to write your email and password in .env

For the authorization you need to start function self.auth() in kwork_parse.py.

## Using
Before starting kwork_parse.py you can set your API keys(MISTRAL_API_KEY, GIGACHAT_API_KEY) and account credentials(KWORK_LOGIN, KWORK_PASSWORD) in the .env file.

## Filtering
For the filtration, you need to authorize in kwork.ru, set the filters and set the way to your browser profile settings in the .env file. `PROFILE_PATH=...`

## How to use

```bash
git clone https://github.com/nkngineer/kwork_parse.git
cd kwork_parse
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python -m parser.parse_kwork.py
```

## Future
- filtering categories
- json-structured answer from the AI
- check relevance of the card by comparing with the current stack
- \* backend wrapper
## Completed
- save card history in database
- hide tasks with expired time
