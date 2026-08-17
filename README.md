# Kwork_parse 
This is the parser of kwork.ru. 

This script process cards of freelance marketplace by the AI(Mistral, Gigachat).
Target of this script - get analyzed test task and print required skills, stack and short description.  
## Login
Before authorization, you need to write your email and password in .env

For the authorization you need to start function self.auth() in kwork_parse.py.
## Filtering
For the filtration, you need to authorize in kwork.ru, set the filters and set the way to your browser profile settings in .env. `PROFILE_PATH=...`
## How to use
```bash
git clone https://github.com/твой-юзернейм/твой-репозиторий.git
cd твой-репозиторий
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```
## Future
- save card history in memory or database
- automatic delete tasks with expired time
- filtering categories