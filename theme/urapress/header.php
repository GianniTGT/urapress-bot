<?php
/**
 * Koka e faqes.
 *
 * @package UraPress
 */
?><!doctype html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#16181D">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link screen-reader-text" href="#content"><?php esc_html_e( 'Kalo te përmbajtja', 'urapress' ); ?></a>

<div class="up-topbar">
	<div class="up-wrap">
		<span><?php echo esc_html( urapress_sq_date( (int) current_time( 'timestamp' ), true ) ); ?></span>
		<span class="up-topbar__slogan"><?php esc_html_e( 'Ura mes Atdheut dhe Dijasporës', 'urapress' ); ?></span>
	</div>
</div>

<header class="up-header">
	<div class="up-wrap up-header__inner">
		<?php urapress_logo( is_front_page() ? 'h1' : 'div' ); ?>
		<div class="up-header__tools">
			<?php get_search_form(); ?>
			<button class="up-menu-toggle" type="button" aria-controls="primary-menu" aria-expanded="false" aria-label="<?php esc_attr_e( 'Hap menynë', 'urapress' ); ?>">
				<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
			</button>
		</div>
	</div>
</header>

<nav class="up-nav" aria-label="<?php esc_attr_e( 'Rubrikat', 'urapress' ); ?>">
	<div class="up-wrap">
		<div class="up-nav__mobile-search"><?php get_search_form(); ?></div>
		<div class="up-nav__inner">
			<?php
			wp_nav_menu(
				array(
					'theme_location' => 'primary',
					'container'      => false,
					'menu_id'        => 'primary-menu',
					'depth'          => 1,
					'fallback_cb'    => 'urapress_fallback_menu',
				)
			);
			?>
		</div>
	</div>
</nav>

<div id="content" class="up-main">
