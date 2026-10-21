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
<meta name="format-detection" content="telephone=no, address=no, email=no, date=no">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<a class="skip-link screen-reader-text" href="#content"><?php esc_html_e( 'Kalo te përmbajtja', 'urapress' ); ?></a>

<?php if ( is_active_sidebar( 'ads-top' ) ) : ?>
<div class="up-adtop" aria-label="<?php esc_attr_e( 'Reklamë', 'urapress' ); ?>">
	<div class="up-wrap up-adtop__inner"><?php dynamic_sidebar( 'ads-top' ); ?></div>
</div>
<?php endif; ?>

<header class="up-header">
	<div class="up-wrap up-header__inner">
		<div class="up-header__left">
			<button class="up-menu-toggle" type="button" aria-controls="primary-menu" aria-expanded="false" aria-label="<?php esc_attr_e( 'Hap menynë', 'urapress' ); ?>">
				<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
			</button>
			<?php get_search_form(); ?>
		</div>
		<div class="up-header__center"><?php urapress_logo( is_front_page() ? 'h1' : 'div' ); ?></div>
		<nav class="up-header__right" aria-label="<?php esc_attr_e( 'Faqet', 'urapress' ); ?>">
			<?php if ( is_user_logged_in() ) : ?>
				<a class="up-header__acc" href="<?php echo esc_url( home_url( '/llogaria/' ) ); ?>">👤<span> Llogaria</span></a>
			<?php else : ?>
				<a class="up-header__acc" href="<?php echo esc_url( urapress_hyr_url() ); ?>" rel="nofollow" aria-label="Hyr">👤<span> Hyr</span></a>
			<?php endif; ?>
			<?php
			$urapress_page = get_page_by_path( 'reklamo' );
			if ( $urapress_page ) {
				printf( '<a href="%s">Reklamo</a>', esc_url( get_permalink( $urapress_page ) ) );
			}
			?>
		</nav>
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
