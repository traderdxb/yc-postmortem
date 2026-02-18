/* ═══════════════════════════════════════════════════════════════════════════
   YC Postmortem — JavaScript
   Voting, Comments, Reply Forms, Anonymity Toggle
   ═══════════════════════════════════════════════════════════════════════════ */

// ─── Voting ───────────────────────────────────────────────────────────────
function vote(itemId, itemType, direction, btn) {
    fetch('/api/vote', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            id: itemId,
            type: itemType,
            direction: direction
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Update the vote count display
            const voteCountEl = btn.parentElement.querySelector('.vote-count');
            if (voteCountEl) {
                voteCountEl.textContent = data.votes;
            }
            // Add voted class for visual feedback
            btn.classList.add('voted');
            // Brief animation
            btn.style.transform = 'scale(1.3)';
            setTimeout(() => { btn.style.transform = 'scale(1)'; }, 150);
        }
    })
    .catch(err => console.error('Vote error:', err));
}

// ─── Comments ─────────────────────────────────────────────────────────────
function submitComment(storyId, parentId) {
    let authorInput, textInput;

    if (parentId) {
        // Reply form
        const replyContainer = document.getElementById('reply-form-' + parentId);
        authorInput = replyContainer.querySelector('.reply-author');
        textInput = replyContainer.querySelector('.reply-text');
    } else {
        // Top-level comment
        authorInput = document.getElementById('comment-author');
        textInput = document.getElementById('comment-text');
    }

    const author = authorInput ? authorInput.value.trim() : 'Anonymous';
    const text = textInput ? textInput.value.trim() : '';

    if (!text) {
        textInput.style.borderColor = '#ef4444';
        textInput.placeholder = 'Please write something...';
        setTimeout(() => {
            textInput.style.borderColor = '';
            textInput.placeholder = textInput.dataset.placeholder || 'Share your thoughts...';
        }, 2000);
        return;
    }

    fetch('/api/comment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            story_id: storyId,
            author: author || 'Anonymous',
            text: text,
            parent_id: parentId
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            // Reload to show new comment (simple approach)
            location.reload();
        }
    })
    .catch(err => console.error('Comment error:', err));
}

// ─── Reply Forms ──────────────────────────────────────────────────────────
function showReplyForm(commentId, storyId) {
    const container = document.getElementById('reply-form-' + commentId);

    // Toggle: if already showing, hide it
    if (container.innerHTML.trim()) {
        container.innerHTML = '';
        return;
    }

    // Close any other open reply forms
    document.querySelectorAll('.reply-form-container').forEach(el => {
        if (el.id !== 'reply-form-' + commentId) {
            el.innerHTML = '';
        }
    });

    container.innerHTML = `
        <div class="comment-form">
            <input type="text" class="reply-author comment-author-input" placeholder="Your name (optional)">
            <textarea class="reply-text comment-textarea" rows="2" placeholder="Write a reply..." data-placeholder="Write a reply..."></textarea>
            <div class="comment-form-actions">
                <button onclick="showReplyForm('${commentId}', '${storyId}')" class="btn btn-sm" style="background:#eee;color:#555;margin-right:6px;">Cancel</button>
                <button onclick="submitComment('${storyId}', '${commentId}')" class="btn btn-primary btn-sm">Reply</button>
            </div>
        </div>
    `;

    // Focus the textarea
    container.querySelector('.reply-text').focus();
}

// ─── Anonymity Toggle ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', function() {
    const anonToggle = document.getElementById('is_anonymous');
    const identityFields = document.getElementById('identity-fields');

    if (anonToggle && identityFields) {
        anonToggle.addEventListener('change', function() {
            if (this.checked) {
                identityFields.style.opacity = '0.4';
                identityFields.style.pointerEvents = 'none';
                identityFields.querySelectorAll('input').forEach(input => {
                    input.value = '';
                    input.placeholder = 'Hidden (anonymous)';
                });
            } else {
                identityFields.style.opacity = '1';
                identityFields.style.pointerEvents = 'auto';
                identityFields.querySelectorAll('input').forEach(input => {
                    input.placeholder = input.id === 'founder_name' ? 'Your full name' : "Your startup's name";
                });
            }
        });
    }

    // Smooth scroll for hero CTA
    const heroBtn = document.querySelector('.btn-hero');
    if (heroBtn) {
        heroBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.getElementById('stories-feed');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    }
});
