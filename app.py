import os
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="YC Postmortem")

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
STORIES_FILE = os.path.join(DATA_DIR, 'stories.json')
COMMENTS_FILE = os.path.join(DATA_DIR, 'comments.json')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')

os.makedirs(DATA_DIR, exist_ok=True)

# Setup templates
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

# In-memory session store (for simplicity - use database in production)
sessions = {}

# Data functions
def load_json(filepath, default=None):
    if default is None:
        default = []
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default
    return default

def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_stories():
    return load_json(STORIES_FILE, [])

def save_stories(stories):
    save_json(STORIES_FILE, stories)

def load_comments():
    return load_json(COMMENTS_FILE, [])

def save_comments(comments):
    save_json(COMMENTS_FILE, comments)

def load_users():
    return load_json(USERS_FILE, {})

def save_users(users):
    save_json(USERS_FILE, users)

def seed_if_needed():
    """Auto-seed database on first visit."""
    stories = load_stories()
    if not stories:
        # Import and run seed
        try:
            import seed_data
            seed_data.seed()
            stories = load_stories()
        except:
            pass
    return stories

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    stories = seed_if_needed()
    
    # Sorting
    sort = request.query_params.get('sort', 'top')
    if sort == 'new':
        stories_sorted = sorted(stories, key=lambda x: x.get('created_at', ''), reverse=True)
    else:
        stories_sorted = sorted(stories, key=lambda x: x.get('votes', 0), reverse=True)
    
    # Filtering
    platform_filter = request.query_params.get('platform', '')
    if platform_filter:
        stories_sorted = [s for s in stories_sorted if s.get('platform', '') == platform_filter]
    
    search_query = request.query_params.get('q', '')
    if search_query:
        stories_sorted = [s for s in stories_sorted if search_query.lower() in s.get('title', '').lower()]
    
    # Get filters
    platforms = sorted(set(s.get('platform', '') for s in stories if s.get('platform')))
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "stories": stories_sorted,
        "platforms": platforms,
        "platform_filter": platform_filter,
        "search_query": search_query,
        "sort": sort
    })

@app.get("/story/{story_id}", response_class=HTMLResponse)
async def story_detail(request: Request, story_id: str):
    stories = load_stories()
    story = next((s for s in stories if s.get('id') == story_id), None)
    
    if not story:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    
    comments = load_comments()
    story_comments = [c for c in comments if c.get('story_id') == story_id]
    
    return templates.TemplateResponse("story_detail.html", {
        "request": request,
        "story": story,
        "comments": story_comments
    })

@app.get("/submit", response_class=HTMLResponse)
async def submit_page(request: Request):
    return templates.TemplateResponse("submit.html", {"request": request})

@app.post("/submit")
async def submit_story(
    request: Request,
    title: str = Form(...),
    platform: str = Form(...),
    rejection_reason: str = Form(...),
    what_learned: str = Form(""),
    advice: str = Form(""),
    batch: str = Form(""),
    tags: str = Form("")
):
    stories = load_stories()
    
    new_story = {
        "id": str(uuid.uuid4()),
        "title": title,
        "platform": platform,
        "rejection_reason": rejection_reason,
        "what_learned": what_learned,
        "advice": advice,
        "batch": batch,
        "tags": [t.strip() for t in tags.split(',') if t.strip()],
        "votes": 0,
        "created_at": datetime.now().isoformat()
    }
    
    stories.append(new_story)
    save_stories(stories)
    
    return RedirectResponse(url=f"/story/{new_story['id']}", status_code=303)

@app.post("/api/vote")
async def vote(request: Request):
    data = await request.json()
    story_id = data.get('story_id')
    
    stories = load_stories()
    for story in stories:
        if story.get('id') == story_id:
            story['votes'] = story.get('votes', 0) + 1
            break
    
    save_stories(stories)
    return {"success": True}

@app.post("/api/comment")
async def add_comment(request: Request):
    data = await request.json()
    story_id = data.get('story_id')
    author = data.get('author', 'Anonymous')
    text = data.get('text', '')
    
    comments = load_comments()
    new_comment = {
        "id": str(uuid.uuid4()),
        "story_id": story_id,
        "author": author,
        "text": text,
        "created_at": datetime.now().isoformat()
    }
    
    comments.append(new_comment)
    save_comments(comments)
    
    return {"success": True, "comment": new_comment}

# Auth routes
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    
    # Check if username exists
    for user_id, user_data in users.items():
        if user_data.get('username') == username:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = str(uuid.uuid4())
    users[user_id] = {
        'username': username,
        'password_hash': password  # In production, use password hashing!
    }
    save_users(users)
    
    return RedirectResponse(url="/login", status_code=303)

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    users = load_users()
    
    for user_id, user_data in users.items():
        if user_data.get('username') == username and user_data.get('password_hash') == password:
            return {"success": True, "username": username}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Serve static files
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
