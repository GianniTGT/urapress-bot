<?php
/**
 * UraPress – funksionet e temës.
 *
 * @package UraPress
 */

defined( 'ABSPATH' ) || exit;

define( 'URAPRESS_VERSION', '1.0.1' );

/**
 * Rubrikat kryesore, në radhën e menysë dhe të faqes kryesore.
 * Emrat duhet të përputhen me kategoritë që krijon bot-i.
 */
function urapress_main_categories() {
	return array(
		'Zvicër',
		'Diaspora',
		'Kosovë',
		'Shqipëri',
		'Maqedoni e Veriut',
		'Mal i Zi',
		'Lugina e Preshevës',
		'Bota',
		'Ekonomi',
		'Sport',
		'Kulturë & Showbiz',
	);
}

/* ------------------------------------------------------------------ */
/* Setup                                                              */
/* ------------------------------------------------------------------ */

function urapress_setup() {
	load_theme_textdomain( 'urapress', get_template_directory() . '/languages' );

	add_theme_support( 'title-tag' );
	add_theme_support( 'post-thumbnails' );
	add_theme_support( 'automatic-feed-links' );
	add_theme_support( 'responsive-embeds' );
	add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption', 'style', 'script' ) );

	add_image_size( 'urapress-lead', 1200, 675, true );
	add_image_size( 'urapress-card', 640, 360, true );
	add_image_size( 'urapress-thumb', 240, 180, true );

	register_nav_menus(
		array(
			'primary' => __( 'Menyja kryesore', 'urapress' ),
			'footer'  => __( 'Menyja e fundit (faqet)', 'urapress' ),
		)
	);
}
add_action( 'after_setup_theme', 'urapress_setup' );

function urapress_content_width() {
	$GLOBALS['content_width'] = 780;
}
add_action( 'after_setup_theme', 'urapress_content_width', 0 );

/* ------------------------------------------------------------------ */
/* Styles & scripts                                                   */
/* ------------------------------------------------------------------ */

function urapress_assets() {
	wp_enqueue_style(
		'urapress-fonts',
		'https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800;900&display=swap',
		array(),
		null
	);
	wp_enqueue_style( 'urapress', get_stylesheet_uri(), array( 'urapress-fonts' ), URAPRESS_VERSION );

	wp_register_script( 'urapress-nav', '', array(), URAPRESS_VERSION, true );
	wp_enqueue_script( 'urapress-nav' );
	wp_add_inline_script(
		'urapress-nav',
		"(function(){var b=document.querySelector('.up-menu-toggle'),n=document.querySelector('.up-nav');if(!b||!n)return;b.addEventListener('click',function(){var o=n.classList.toggle('is-open');b.setAttribute('aria-expanded',o?'true':'false');});})();"
	);
}
add_action( 'wp_enqueue_scripts', 'urapress_assets' );

function urapress_preconnect( $urls, $relation_type ) {
	if ( 'preconnect' === $relation_type ) {
		$urls[] = array( 'href' => 'https://fonts.gstatic.com', 'crossorigin' );
	}
	return $urls;
}
add_filter( 'wp_resource_hints', 'urapress_preconnect', 10, 2 );

/* Favicon me harkun, nëse nuk është vendosur "Site Icon" në WordPress. */
function urapress_favicon() {
	if ( has_site_icon() ) {
		return;
	}
	printf( '<link rel="icon" type="image/svg+xml" href="%s">' . "\n", esc_url( get_template_directory_uri() . '/assets/favicon.svg' ) );
}
add_action( 'wp_head', 'urapress_favicon' );

/* ------------------------------------------------------------------ */
/* Widget areas                                                       */
/* ------------------------------------------------------------------ */

function urapress_widgets() {
	register_sidebar(
		array(
			'name'          => __( 'Shiriti anësor', 'urapress' ),
			'id'            => 'sidebar-1',
			'description'   => __( 'Shfaqet në artikuj dhe rubrika.', 'urapress' ),
			'before_widget' => '<section id="%1$s" class="up-widget %2$s">',
			'after_widget'  => '</section>',
			'before_title'  => '<div class="up-section__head"><h2 class="up-section__title">',
			'after_title'   => '</h2></div>',
		)
	);
	register_sidebar(
		array(
			'name'          => __( 'Reklamë – faqja kryesore', 'urapress' ),
			'id'            => 'ads-home',
			'description'   => __( 'Shfaqet në faqen kryesore pas lajmeve të fundit.', 'urapress' ),
			'before_widget' => '<div id="%1$s" class="up-ad %2$s">',
			'after_widget'  => '</div>',
			'before_title'  => '<div class="up-ad__label">',
			'after_title'   => '</div>',
		)
	);
}
add_action( 'widgets_init', 'urapress_widgets' );

/* ------------------------------------------------------------------ */
/* Excerpt                                                            */
/* ------------------------------------------------------------------ */

add_filter( 'excerpt_length', fn() => 26, 999 );
add_filter( 'excerpt_more', fn() => '…' );

/* ------------------------------------------------------------------ */
/* Helpers                                                            */
/* ------------------------------------------------------------------ */

/** Logoja: "ura" në të kuqe, "press" në të zezë, me harkun e urës poshtë. */
function urapress_logo( $tag = 'div' ) {
	$tag = in_array( $tag, array( 'h1', 'div' ), true ) ? $tag : 'div';
	printf(
		'<%1$s class="up-logo-wrap" style="margin:0"><a class="up-logo" href="%2$s" rel="home" aria-label="%3$s">' .
		'<span class="up-logo__word" aria-hidden="true"><span>ura</span>press</span>' .
		'<svg class="up-logo__arch" viewBox="0 0 560 56" aria-hidden="true"><path d="M14 14 Q280 64 546 14" fill="none" stroke="#D7141A" stroke-width="8" stroke-linecap="round"/><circle cx="14" cy="14" r="10" fill="currentColor"/><circle cx="546" cy="14" r="10" fill="currentColor"/></svg>' .
		'</a></%1$s>',
		$tag,
		esc_url( home_url( '/' ) ),
		esc_attr( get_bloginfo( 'name' ) )
	);
}

/** Kategoria kryesore e artikullit (e para që është në listën e rubrikave). */
function urapress_primary_category( $post_id = null ) {
	$cats = get_the_category( $post_id );
	if ( empty( $cats ) ) {
		return null;
	}
	$order = array_map( 'mb_strtolower', urapress_main_categories() );
	usort(
		$cats,
		function ( $a, $b ) use ( $order ) {
			$ia = array_search( mb_strtolower( html_entity_decode( $a->name ) ), $order, true );
			$ib = array_search( mb_strtolower( html_entity_decode( $b->name ) ), $order, true );
			return ( false === $ia ? 99 : $ia ) <=> ( false === $ib ? 99 : $ib );
		}
	);
	foreach ( $cats as $cat ) {
		if ( 'uncategorized' !== $cat->slug && 'pa-kategori' !== $cat->slug ) {
			return $cat;
		}
	}
	return $cats[0];
}

/**
 * Data në shqip, pavarësisht gjuhës së WordPress.
 * $ts = timestamp lokal (si nga current_time / get_post_time pa GMT).
 */
function urapress_sq_date( $ts, $with_weekday = false, $with_time = false ) {
	$months = array( 1 => 'janar', 'shkurt', 'mars', 'prill', 'maj', 'qershor', 'korrik', 'gusht', 'shtator', 'tetor', 'nëntor', 'dhjetor' );
	$days   = array( 'E diel', 'E hënë', 'E martë', 'E mërkurë', 'E enjte', 'E premte', 'E shtunë' );
	$out    = (int) gmdate( 'j', $ts ) . ' ' . $months[ (int) gmdate( 'n', $ts ) ] . ' ' . gmdate( 'Y', $ts );
	if ( $with_weekday ) {
		$out = $days[ (int) gmdate( 'w', $ts ) ] . ', ' . $out;
	}
	if ( $with_time ) {
		$out .= ', ' . gmdate( 'H:i', $ts );
	}
	return $out;
}

/** Koha e publikimit: "2 orë më parë" për lajmet e fundit, përndryshe data. */
function urapress_time( $post_id = null ) {
	$gmt  = (int) get_post_time( 'U', true, $post_id );
	$diff = time() - $gmt;
	if ( $diff < HOUR_IN_SECONDS ) {
		$min  = max( 1, (int) round( $diff / MINUTE_IN_SECONDS ) );
		$text = sprintf( '%d %s më parë', $min, 1 === $min ? 'minutë' : 'minuta' );
	} elseif ( $diff < DAY_IN_SECONDS ) {
		$h    = (int) round( $diff / HOUR_IN_SECONDS );
		$text = sprintf( '%d orë më parë', $h );
	} else {
		$text = urapress_sq_date( (int) get_post_time( 'U', false, $post_id ) );
	}
	return sprintf( '<time datetime="%s">%s</time>', esc_attr( get_the_date( 'c', $post_id ) ), esc_html( $text ) );
}

/** Kategoria e gjetur sipas emrit (p.sh. "Zvicër"). */
function urapress_category_by_name( $name ) {
	$term = get_term_by( 'name', $name, 'category' );
	if ( ! $term ) {
		$term = get_term_by( 'slug', sanitize_title( $name ), 'category' );
	}
	return $term ?: null;
}

/** A është foto ilustruese e krijuar me AI? (sipas legjendës së fotos) */
function urapress_is_ai_image( $attachment_id ) {
	$caption = wp_get_attachment_caption( $attachment_id );
	return $caption && false !== stripos( $caption, '(AI)' );
}

/** Menyja rezervë: rubrikat kryesore, nëse nuk është caktuar meny në WordPress. */
function urapress_fallback_menu() {
	echo '<ul id="primary-menu">';
	foreach ( urapress_main_categories() as $name ) {
		$term = urapress_category_by_name( $name );
		if ( ! $term ) {
			continue;
		}
		$current = is_category( $term->term_id ) ? 'current-cat' : '';
		printf( '<li class="%s"><a href="%s">%s</a></li>', esc_attr( $current ), esc_url( get_category_link( $term ) ), esc_html( $term->name ) );
	}
	echo '</ul>';
}

/** IDs e artikujve që janë shfaqur tashmë në faqen kryesore (pa dublime). */
function urapress_shown( $add = null ) {
	static $ids = array();
	if ( null !== $add ) {
		$ids = array_merge( $ids, (array) $add );
	}
	return $ids;
}

/* ------------------------------------------------------------------ */
/* Open Graph – për ndarje të bukur në WhatsApp / Facebook            */
/* ------------------------------------------------------------------ */

function urapress_open_graph() {
	if ( defined( 'WPSEO_VERSION' ) || defined( 'RANK_MATH_VERSION' ) || class_exists( 'SEOPress\Core\Kernel' ) ) {
		return; // një plugin SEO e bën këtë vetë
	}
	$title = wp_get_document_title();
	$desc  = get_bloginfo( 'description' );
	$url   = home_url( add_query_arg( array() ) );
	$image = '';
	$type  = 'website';

	if ( is_singular() ) {
		$post  = get_queried_object();
		$title = get_the_title( $post );
		$desc  = has_excerpt( $post ) ? get_the_excerpt( $post ) : wp_trim_words( wp_strip_all_tags( $post->post_content ), 30, '…' );
		$url   = get_permalink( $post );
		$type  = 'article';
		if ( has_post_thumbnail( $post ) ) {
			$image = get_the_post_thumbnail_url( $post, 'urapress-lead' );
		}
	}

	$tags = array(
		'og:site_name'   => get_bloginfo( 'name' ),
		'og:locale'      => 'sq_AL',
		'og:type'        => $type,
		'og:title'       => $title,
		'og:description' => $desc,
		'og:url'         => $url,
		'og:image'       => $image,
		'twitter:card'   => $image ? 'summary_large_image' : 'summary',
	);
	foreach ( $tags as $prop => $content ) {
		if ( '' === $content ) {
			continue;
		}
		$attr = 0 === strpos( $prop, 'twitter:' ) ? 'name' : 'property';
		printf( '<meta %s="%s" content="%s">' . "\n", $attr, esc_attr( $prop ), esc_attr( $content ) );
	}
}
add_action( 'wp_head', 'urapress_open_graph', 5 );
