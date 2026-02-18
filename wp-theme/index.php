<?php get_header(); ?>

<!-- Filter Bar -->
<div class="filter-bar">
    <a href="<?php echo esc_url(home_url('/')); ?>" class="filter-item <?php if (!isset($_GET['platform'])) echo 'active'; ?>">All</a>
    <?php
    $platforms = get_terms(array('taxonomy' => 'platform', 'hide_empty' => true));
    foreach ($platforms as $platform) :
        $active = isset($_GET['platform']) && $_GET['platform'] == $platform->slug ? 'active' : '';
    ?>
        <a href="<?php echo esc_url(add_query_arg('platform', $platform->slug)); ?>" class="filter-item <?php echo $active; ?>">
            <?php echo esc_html($platform->name); ?> (<?php echo $platform->count; ?>)
        </a>
    <?php endforeach; ?>
</div>

<!-- Stories Grid -->
<div class="stories-grid">
    <?php if (have_posts()) : ?>
        <?php while (have_posts()) : the_post(); ?>
            <article class="story-card">
                <div class="story-header">
                    <h2 class="story-title">
                        <a href="<?php the_permalink(); ?>"><?php the_title(); ?></a>
                    </h2>
                    <?php 
                    $platforms = get_the_terms(get_the_ID(), 'platform');
                    if ($platforms && !is_wp_error($platforms)) :
                        echo '<span class="platform-badge">' . esc_html($platforms[0]->name) . '</span>';
                    endif;
                    ?>
                </div>
                
                <div class="story-meta">
                    <?php 
                    $company_name = get_post_meta(get_the_ID(), 'company_name', true);
                    if ($company_name) :
                        echo '<span>' . esc_html($company_name) . '</span>';
                    endif;
                    ?>
                    <span><?php echo get_the_date('M j, Y'); ?></span>
                </div>
                
                <div class="story-excerpt">
                    <?php the_excerpt(); ?>
                </div>
                
                <div class="story-footer">
                    <button class="vote-btn">
                        <span>▲</span>
                        <span class="vote-count"><?php echo get_post_meta(get_the_ID(), 'votes', true) ?: 0; ?></span>
                    </button>
                    <a href="<?php the_permalink(); ?>" class="btn btn-ghost">Read More →</a>
                </div>
            </article>
        <?php endwhile; ?>
    <?php else : ?>
        <p>No stories found. Be the first to share your rejection story!</p>
    <?php endif; ?>
</div>

<!-- Pagination -->
<div class="pagination">
    <?php 
    echo paginate_links(array(
        'prev_text' => '&laquo; Previous',
        'next_text' => 'Next &raquo;',
    ));
    ?>
</div>

<?php get_footer(); ?>
