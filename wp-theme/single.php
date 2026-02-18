<?php get_header(); ?>

<!-- Story Detail Page -->
<article class="story-detail">
    <div class="story-content">
        <div class="story-header">
            <h1 class="story-title"><?php the_title(); ?></h1>
            
            <div class="story-meta">
                <?php 
                $company_name = get_post_meta(get_the_ID(), 'company_name', true);
                if ($company_name) :
                    echo '<span>' . esc_html($company_name) . '</span>';
                endif;
                
                $platforms = get_the_terms(get_the_ID(), 'platform');
                if ($platforms && !is_wp_error($platforms)) :
                    echo '<span class="platform-badge">' . esc_html($platforms[0]->name) . '</span>';
                endif;
                
                $batches = get_the_terms(get_the_ID(), 'batch');
                if ($batches && !is_wp_error($batches)) :
                    echo '<span>' . esc_html($batches[0]->name) . ' Batch</span>';
                endif;
                ?>
                <span><?php echo get_the_date('F j, Y'); ?></span>
            </div>
        </div>
        
        <!-- Rejection Reason Banner -->
        <?php 
        $rejection_reason = get_post_meta(get_the_ID(), 'rejection_reason', true);
        if ($rejection_reason) :
        ?>
        <div class="rejection-reason-banner">
            <span class="reason-icon">🚫</span>
            <div>
                <span class="reason-label">Rejection Reason</span>
                <div class="reason-text"><?php echo esc_html($rejection_reason); ?></div>
            </div>
        </div>
        <?php endif; ?>
        
        <!-- Main Content -->
        <div class="story-body">
            <?php the_content(); ?>
        </div>
        
        <!-- Vote Section -->
        <div class="vote-section">
            <button class="vote-btn" onclick="alert('Thanks for voting!')">
                <span>▲</span>
                <span class="vote-count"><?php echo get_post_meta(get_the_ID(), 'votes', true) ?: 0; ?></span>
                <span>Upvote this story</span>
            </button>
        </div>
        
        <!-- Tags -->
        <?php 
        $tags = get_the_tags();
        if ($tags) :
        ?>
        <div class="story-tags">
            <?php foreach ($tags as $tag) : ?>
                <span class="tag"><?php echo esc_html($tag->name); ?></span>
            <?php endforeach; ?>
        </div>
        <?php endif; ?>
    </div>
    
    <!-- Comments Section -->
    <div class="comments-section">
        <h3>Discussion (<?php comments_number('0', '1', '%'); ?>)</h3>
        
        <?php 
        if (comments_open() || get_comments_number()) :
            comments_template();
        endif;
        ?>
        
        <?php if (is_user_logged_in()) : ?>
        <form class="comment-form" method="post">
            <div class="form-group">
                <textarea name="comment" rows="4" placeholder="Share your thoughts..."></textarea>
            </div>
            <button type="submit" class="btn btn-primary">Post Comment</button>
        </form>
        <?php else : ?>
        <p><a href="<?php echo wp_login_url(get_permalink()); ?>">Log in</a> to leave a comment.</p>
        <?php endif; ?>
    </div>
</article>

<?php get_footer(); ?>
