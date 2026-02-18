<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
    
    <!-- Navigation -->
    <nav class="navbar">
        <div class="nav-inner">
            <a href="<?php echo esc_url(home_url('/')); ?>" class="nav-logo">
                <span class="logo-icon">▲</span>
                <span class="logo-text"><?php bloginfo('name'); ?></span>
            </a>
            
            <div class="nav-actions">
                <?php if (is_user_logged_in()) : ?>
                    <span style="margin-right: 1rem; color: var(--text-secondary);">
                        Hello, <?php $current_user = wp_get_current_user(); echo esc_html($current_user->display_name); ?>
                    </span>
                    <a href="<?php echo wp_logout_url(home_url()); ?>" class="btn btn-ghost">Logout</a>
                    <a href="<?php echo esc_url(home_url('/submit')); ?>" class="btn btn-primary">+ Submit Story</a>
                <?php else : ?>
                    <a href="<?php echo wp_login_url(); ?>" class="btn btn-ghost">Log In</a>
                    <a href="<?php echo wp_registration_url(); ?>" class="btn btn-primary">Sign Up</a>
                <?php endif; ?>
            </div>
        </div>
    </nav>

    <?php if (is_front_page()) : ?>
    <!-- Hero Section -->
    <header class="hero">
        <h1>Learn from the <span class="highlight">"No"</span></h1>
        <p class="hero-subtitle">Real rejection stories from founders who applied to YC, Techstars, 500 Startups, and more. The post-game analysis the startup world needs.</p>
        <p class="hero-subtitle">Every rejection is a lesson. Founders share their YC rejection reasons and what they'd tell future applicants to do differently.</p>
    </header>
    <?php endif; ?>
    
    <main class="container">
