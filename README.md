# Google Square Hackathon

## 1. Create virtual environment
```bash
python3 -m venv venv
```
## 2. Activate virtual environment
```bash
source venv/bin/activate
```
## 3. Install requirements
```bash
pip install -r requirements.txt
```
## 4. Export environment variables
```bash
GOOGLE_APPLICATION_CREDENTIALS=<path to service account json file>
SQUARE_ACCESS_TOKEN=<square access token>
SUPABASE_DB=<supabase db password>
```
## 5. Run server
```bash
uvicorn app.main:app --reload
```
