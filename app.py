import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
STORIES_FILE = os.path.join(DATA_DIR, 'stories.json')
COMMENTS_FILE = os.path.join(DATA_DIR, 'comments.json')

os.makedirs(DATA_DIR, exist_ok=True)


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


def seed_if_needed():
    """Auto-seed database on first visit."""
    stories = load_stories()
    if len(stories) == 0:
        from seed_data import get_seed_stories, get_seed_comments
        stories = get_seed_stories()
        save_stories(stories)
        comments = get_seed_comments(stories)
        save_comments(comments)
    return stories


def get_rejection_reason_stats(stories):
    """Calculate rejection reason percentages for sidebar."""
    reasons = {}
    for s in stories:
        reason = s.get('rejection_reason', 'Unknown')
        reasons[reason] = reasons.get(reason, 0) + 1
    total = len(stories)
    stats = []
    for reason, count in sorted(reasons.items(), key=lambda x: -x[1]):
        stats.append({
            'reason': reason,
            'count': count,
            'percent': round(count / total * 100) if total > 0 else 0
        })
    return stats[:10]


def get_platform_stats(stories):
    """Calculate platform distribution."""
    platforms = {}
    for s in stories:
        p = s.get('platform', 'Unknown')
        platforms[p] = platforms.get(p, 0) + 1
    return dict(sorted(platforms.items(), key=lambda x: -x[1]))


def get_all_tags(stories):
    """Get all unique tags."""
    tags = set()
    for s in stories:
        for t in s.get('tags', []):
            tags.add(t)
    return sorted(tags)


def get_all_batches(stories):
    """Get all unique batches."""
    batches = set()
    for s in stories:
        b = s.get('batch', '')
        if b:
            batches.add(b)
    return sorted(batches, reverse=True)


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    stories = seed_if_needed()

    # Sorting
    sort = request.args.get('sort', 'top')
    if sort == 'new':
        stories_sorted = sorted(stories, key=lambda x: x.get('created_at', ''), reverse=True)
    else:  # top
        stories_sorted = sorted(stories, key=lambda x: x.get('votes', 0), reverse=True)

    # Filtering
    platform_filter = request.args.get('platform', '')
    tag_filter = request.args.get('tag', '')
    batch_filter = request.args.get('batch', '')
    search_query = request.args.get('q', '')

    if platform_filter:
        stories_sorted = [s for s in stories_sorted if s.get('platform') == platform_filter]
    if tag_filter:
        stories_sorted = [s for s in stories_sorted if tag_filter in s.get('tags', [])]
    if batch_filter:
        stories_sorted = [s for s in stories_sorted if s.get('batch') == batch_filter]
    if search_query:
        q = search_query.lower()
        stories_sorted = [s for s in stories_sorted if
                          q in s.get('title', '').lower() or
                          q in s.get('story', '').lower() or
                          q in s.get('key_learning', '').lower() or
                          q in s.get('company_name', '').lower() or
                          q in s.get('founder_name', '').lower()]

    # Stats for sidebar
    reason_stats = get_rejection_reason_stats(stories)
    platform_stats = get_platform_stats(stories)
    all_tags = get_all_tags(stories)
    all_batches = get_all_batches(stories)

    return render_template('index.html',
                           stories=stories_sorted,
                           total_stories=len(stories),
                           sort=sort,
                           platform_filter=platform_filter,
                           tag_filter=tag_filter,
                           batch_filter=batch_filter,
                           search_query=search_query,
                           reason_stats=reason_stats,
                           platform_stats=platform_stats,
                           all_tags=all_tags,
                           all_batches=all_batches)


@app.route('/story/<story_id>')
def story_detail(story_id):
    stories = seed_if_needed()
    story = next((s for s in stories if s['id'] == story_id), None)
    if not story:
        abort(404)

    comments = load_comments()
    story_comments = [c for c in comments if c.get('story_id') == story_id]

    # Build threaded comments
    top_level = [c for c in story_comments if c.get('parent_id') is None]
    top_level.sort(key=lambda x: x.get('votes', 0), reverse=True)

    def get_replies(parent_id):
        replies = [c for c in story_comments if c.get('parent_id') == parent_id]
        replies.sort(key=lambda x: x.get('created_at', ''))
        return replies

    return render_template('story_detail.html',
                           story=story,
                           comments=top_level,
                           get_replies=get_replies,
                           total_comments=len(story_comments))


@app.route('/submit', methods=['GET', 'POST'])
def submit_story():
    if request.method == 'GET':
        return render_template('submit.html')

    # POST - handle form submission
    data = request.form
    new_story = {
        'id': str(uuid.uuid4())[:8],
        'founder_name': data.get('founder_name', 'Anonymous') if data.get('is_anonymous') != 'on' else 'Anonymous',
        'company_name': data.get('company_name', 'Stealth Startup') if data.get('is_anonymous') != 'on' else 'Stealth Startup',
        'is_anonymous': data.get('is_anonymous') == 'on',
        'platform': data.get('platform', 'Y Combinator'),
        'batch': data.get('batch', ''),
        'reviewer': data.get('reviewer', ''),
        'rejection_date': data.get('rejection_date', ''),
        'category': data.get('category', ''),
        'tags': [t.strip() for t in data.get('tags', '').split(',') if t.strip()],
        'title': data.get('title', ''),
        'rejection_reason': data.get('rejection_reason', ''),
        'story': data.get('story', ''),
        'key_learning': data.get('key_learning', ''),
        'advice_for_applicants': data.get('advice_for_applicants', ''),
        'votes': 0,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }

    stories = load_stories()
    stories.append(new_story)
    save_stories(stories)

    return redirect(url_for('story_detail', story_id=new_story['id']))


@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.get_json()
    item_type = data.get('type', 'story')  # 'story' or 'comment'
    item_id = data.get('id')
    direction = data.get('direction', 'up')

    if item_type == 'story':
        stories = load_stories()
        for s in stories:
            if s['id'] == item_id:
                if direction == 'up':
                    s['votes'] = s.get('votes', 0) + 1
                else:
                    s['votes'] = max(0, s.get('votes', 0) - 1)
                save_stories(stories)
                return jsonify({'success': True, 'votes': s['votes']})
    else:
        comments = load_comments()
        for c in comments:
            if c['id'] == item_id:
                if direction == 'up':
                    c['votes'] = c.get('votes', 0) + 1
                else:
                    c['votes'] = max(0, c.get('votes', 0) - 1)
                save_comments(comments)
                return jsonify({'success': True, 'votes': c['votes']})

    return jsonify({'success': False}), 404


@app.route('/api/comment', methods=['POST'])
def add_comment():
    data = request.get_json()
    story_id = data.get('story_id')
    author = data.get('author', 'Anonymous')
    text = data.get('text', '').strip()
    parent_id = data.get('parent_id')

    if not text or not story_id:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    new_comment = {
        'id': 'c' + str(uuid.uuid4())[:7],
        'story_id': story_id,
        'author': author or 'Anonymous',
        'text': text,
        'parent_id': parent_id,
        'votes': 0,
        'created_at': datetime.utcnow().isoformat() + 'Z'
    }

    comments = load_comments()
    comments.append(new_comment)
    save_comments(comments)

    return jsonify({'success': True, 'comment': new_comment})


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, port=5000)
