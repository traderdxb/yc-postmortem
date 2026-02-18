<?php
/**
 * YC Postmortem Theme Functions
 */

// Enqueue styles and scripts
function yc_postmortem_enqueue_scripts() {
    wp_enqueue_style('yc-postmortem-style', get_stylesheet_uri());
    wp_enqueue_style('google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500&display=swap', array(), null);
}
add_action('wp_enqueue_scripts', 'yc_postmortem_enqueue_scripts');

// Theme setup
function yc_postmortem_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
    
    register_nav_menus(array(
        'primary' => __('Primary Menu', 'yc-postmortem'),
        'footer' => __('Footer Menu', 'yc-postmortem'),
    ));
}
add_action('after_setup_theme', 'yc_postmortem_setup');

// Custom post type for stories
function yc_register_story_post_type() {
    register_post_type('story', array(
        'labels' => array(
            'name' => __('Stories', 'yc-postmortem'),
            'singular_name' => __('Story', 'yc-postmortem'),
            'add_new' => __('Add New Story', 'yc-postmortem'),
            'add_new_item' => __('Add New Story', 'yc-postmortem'),
            'edit_item' => __('Edit Story', 'yc-postmortem'),
            'new_item' => __('New Story', 'yc-postmortem'),
            'view_item' => __('View Story', 'yc-postmortem'),
            'search_items' => __('Search Stories', 'yc-postmortem'),
        ),
        'public' => true,
        'has_archive' => true,
        'show_in_rest' => true,
        'supports' => array('title', 'editor', 'excerpt', 'thumbnail', 'custom-fields'),
        'menu_icon' => 'dashicons-admin-story',
        'rewrite' => array('slug' => 'stories'),
    ));
}
add_action('init', 'yc_register_story_post_type');

// Custom taxonomies
function yc_register_taxonomies() {
    register_taxonomy('platform', 'story', array(
        'labels' => array(
            'name' => __('Platforms', 'yc-postmortem'),
            'singular_name' => __('Platform', 'yc-postmortem'),
        ),
        'hierarchical' => true,
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'platform'),
    ));
    
    register_taxonomy('batch', 'story', array(
        'labels' => array(
            'name' => __('Batches', 'yc-postmortem'),
            'singular_name' => __('Batch', 'yc-postmortem'),
        ),
        'hierarchical' => true,
        'show_in_rest' => true,
        'rewrite' => array('slug' => 'batch'),
    ));
}
add_action('init', 'yc_register_taxonomies');

// Add meta boxes for story data
function yc_add_story_meta_boxes() {
    add_meta_box('story_details', 'Story Details', 'yc_story_details_callback', 'story', 'normal', 'high');
}
add_action('add_meta_boxes', 'yc_add_story_meta_boxes');

function yc_story_details_callback($post) {
    $rejection_reason = get_post_meta($post->ID, 'rejection_reason', true);
    $company_name = get_post_meta($post->ID, 'company_name', true);
    $founder_name = get_post_meta($post->ID, 'founder_name', true);
    $votes = get_post_meta($post->ID, 'votes', true);
    ?>
    <p>
        <label>Company Name:</label>
        <input type="text" name="company_name" value="<?php echo esc_attr($company_name); ?>" style="width:100%">
    </p>
    <p>
        <label>Founder Name (optional):</label>
        <input type="text" name="founder_name" value="<?php echo esc_attr($founder_name); ?>" style="width:100%">
    </p>
    <p>
        <label>Rejection Reason:</label>
        <textarea name="rejection_reason" rows="3" style="width:100%"><?php echo esc_textarea($rejection_reason); ?></textarea>
    </p>
    <p>
        <label>Votes:</label>
        <input type="number" name="votes" value="<?php echo esc_attr($votes); ?>" style="width:100px">
    </p>
    <?php
}

function yc_save_story_meta($post_id) {
    if (array_key_exists('company_name', $_POST)) {
        update_post_meta($post_id, 'company_name', sanitize_text_field($_POST['company_name']));
    }
    if (array_key_exists('founder_name', $_POST)) {
        update_post_meta($post_id, 'founder_name', sanitize_text_field($_POST['founder_name']));
    }
    if (array_key_exists('rejection_reason', $_POST)) {
        update_post_meta($post_id, 'rejection_reason', sanitize_textarea_field($_POST['rejection_reason']));
    }
    if (array_key_exists('votes', $_POST)) {
        update_post_meta($post_id, 'votes', intval($_POST['votes']));
    }
}
add_action('save_post', 'yc_save_story_meta');

// Sidebar widgets
function yc_widgets_init() {
    register_sidebar(array(
        'name' => __('Sidebar', 'yc-postmortem'),
        'id' => 'sidebar-1',
        'description' => __('Add widgets here.', 'yc-postmortem'),
        'before_widget' => '<div class="widget %2$s">',
        'after_widget' => '</div>',
        'before_title' => '<h3 class="widget-title">',
        'after_title' => '</h3>',
    ));
}
add_action('widgets_init', 'yc_widgets_init');
