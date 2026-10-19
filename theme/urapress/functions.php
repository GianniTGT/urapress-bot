<?php
/**
 * UraPress – funksionet e temës.
 *
 * @package UraPress
 */

defined( 'ABSPATH' ) || exit;

define( 'URAPRESS_VERSION', '1.6.0' );

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
	add_theme_support( 'html5', array( 'search-form', 'comment-form', 'comment-list', 'gallery', 'caption', 'style', 'script' ) );

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

/* Rubrikat krijohen automatikisht një herë, që menyja të jetë e plotë që në fillim. */
function urapress_ensure_categories() {
	if ( get_option( 'urapress_cats_v1' ) ) {
		return;
	}
	foreach ( urapress_main_categories() as $name ) {
		if ( ! urapress_category_by_name( $name ) ) {
			wp_insert_term( $name, 'category' );
		}
	}
	update_option( 'urapress_cats_v1', 1 );
}
add_action( 'after_switch_theme', 'urapress_ensure_categories' );
add_action( 'admin_init', 'urapress_ensure_categories' );

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

	// Leuchtendes Tiff-Logo-Aufblitzen (zufällig, einmal pro Besuch). Braucht die Glow-Engine.
	$ads_dir = get_template_directory_uri() . '/assets/ads/';
	wp_enqueue_script( 'urapress-glow', $ads_dir . 'glow.js', array(), URAPRESS_VERSION, true );
	wp_enqueue_script( 'urapress-flash', $ads_dir . 'tiff-flash.js', array( 'urapress-glow' ), URAPRESS_VERSION, true );
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

/** Artikel-IDs für den Aufmacher, nach Rubrik gemischt – damit oben verschiedene Themen sichtbar sind. */
function urapress_diverse_ids( $count, $pool = 24 ) {
	$q = new WP_Query(
		array(
			'posts_per_page'      => $pool,
			'post_status'         => 'publish',
			'ignore_sticky_posts' => false,
			'fields'              => 'ids',
		)
	);
	$picked = array();
	$used   = array();
	$rest   = array();
	foreach ( $q->posts as $id ) {
		$cat = urapress_primary_category( $id );
		$key = $cat ? $cat->term_id : 0;
		if ( count( $picked ) < $count && ! in_array( $key, $used, true ) ) {
			$picked[] = $id;
			$used[]   = $key;
		} else {
			$rest[] = $id;
		}
	}
	foreach ( $rest as $id ) {
		if ( count( $picked ) >= $count ) {
			break;
		}
		$picked[] = $id;
	}
	return array_slice( $picked, 0, $count );
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

/* ------------------------------------------------------------------ */
/* Reklamat e veta (house ads) – ndrysho tekstet/lidhjet këtu          */
/* ------------------------------------------------------------------ */

function urapress_default_ads() {
	return array(
		array(
			'id'     => 'ride2balkan',
			'url'    => 'https://ride2balkan.com',
			'accent' => '#138A5E',
			'kicker' => 'Udhëto në atdhe',
			'title'  => 'Bern → Pejë, Luzern → Gjakovë: gjej udhëtim me bashkëudhëtarë',
			'text'   => 'Ndaj shpenzimet e rrugës drejt Ballkanit – transparente dhe e sigurt. Çdo udhëtim i 11-të pa tarifë shërbimi.',
			'cta'    => 'Gjej udhëtim',
		),
		array(
			'id'     => 'tiffcore',
			'url'    => 'https://tiffcore.ch',
			'accent' => '#17694A',
			'kicker' => 'Për firmat e sanitarisë dhe ngrohjes',
			'title'  => 'Nga raporti në kantier deri te fatura QR – TiffCore',
			'text'   => 'Monteri e regjistron në celular, zyra e faturon. Pa instalim, mbështetje nga Berna. 30 ditë falas.',
			'cta'    => 'Provo falas',
		),
		array(
			'id'     => 'tiffcar',
			'url'    => 'https://tiffcar.ch',
			'accent' => '#0F7A6E',
			'kicker' => 'Për auto-sallone dhe servise veturash',
			'title'  => 'Veturat, klientët dhe shitjet nën kontroll',
			'text'   => 'TiffCar e lehtëson punën e përditshme të auto-salloneve dhe serviseve të veturave – nga pranimi i veturës deri te fatura.',
			'cta'    => 'Zbulo TiffCar',
		),
		array(
			'id'     => 'aino',
			'url'    => 'https://ainohaustechnik.ch',
			'accent' => '#E8501F',
			'kicker' => 'Sanitari & ngrohje në Bernë',
			'title'  => 'Banjo e re, boiler apo defekt urgjent? AINO Haustechnik',
			'text'   => 'Riparime, servis dhe rinovim banjoje e kuzhine – në Bernë dhe rrethinë. Ofertë e qartë, punë e pastër.',
			'cta'    => 'Kërko ofertë',
		),
		array(
			'id'     => 'tiff',
			'url'    => 'https://tiff-software-solutions.com',
			'accent' => '#16181D',
			'kicker' => 'Softuer nga Zvicra',
			'title'  => 'Zgjidhje digjitale për biznesin tënd',
			'text'   => 'Aplikacione, ueb-faqe dhe softuer sipas nevojës – nga TIFF Software Solutions.',
			'cta'    => 'Na kontaktoni',
		),
	);
}


/* Reklamat menaxhohen në WordPress: menyja "Reklamat". */
function urapress_register_ads() {
	register_post_type(
		'urapress_ad',
		array(
			'labels'        => array(
				'name'               => 'Reklamat',
				'singular_name'      => 'Reklamë',
				'add_new'            => 'Neue Anzeige',
				'add_new_item'       => 'Neue Anzeige erstellen',
				'edit_item'          => 'Anzeige bearbeiten',
				'all_items'          => 'Alle Anzeigen',
				'featured_image'     => 'Bild der Anzeige',
				'set_featured_image' => 'Bild wählen',
			),
			'public'        => false,
			'show_ui'       => true,
			'show_in_menu'  => true,
			'menu_position' => 21,
			'menu_icon'     => 'dashicons-megaphone',
			'supports'      => array( 'title', 'thumbnail' ),
		)
	);
}
add_action( 'init', 'urapress_register_ads' );

function urapress_ad_fields() {
	return array(
		'kicker' => array( 'Zeile über dem Titel (klein, farbig)', 'text' ),
		'text'   => array( 'Text (1–2 Sätze)', 'textarea' ),
		'cta'    => array( 'Beschriftung des Buttons', 'text' ),
		'url'    => array( 'Link (https://…)', 'url' ),
		'accent' => array( 'Farbe', 'color' ),
	);
}

function urapress_ad_metabox() {
	add_meta_box(
		'urapress_ad_box',
		'Inhalt der Anzeige',
		function ( $post ) {
			wp_nonce_field( 'urapress_ad_save', 'urapress_ad_nonce' );
			echo '<p style="color:#555">Der <strong>Titel</strong> oben ist die Schlagzeile. Das Bild setzt du rechts unter „Bild der Anzeige“ (ideal 800×450). Aktiv = veröffentlicht, pausieren = als Entwurf speichern.</p>';
			foreach ( urapress_ad_fields() as $key => list( $label, $type ) ) {
				$val = get_post_meta( $post->ID, '_up_ad_' . $key, true );
				if ( 'accent' === $key && ! $val ) {
					$val = '#D7141A';
				}
				printf( '<p><label for="up_ad_%1$s" style="display:block;font-weight:600;margin-bottom:4px">%2$s</label>', esc_attr( $key ), esc_html( $label ) );
				if ( 'textarea' === $type ) {
					printf( '<textarea id="up_ad_%1$s" name="up_ad_%1$s" rows="3" style="width:100%%">%2$s</textarea></p>', esc_attr( $key ), esc_textarea( $val ) );
				} else {
					printf( '<input id="up_ad_%1$s" name="up_ad_%1$s" type="%2$s" value="%3$s" style="%4$s"></p>', esc_attr( $key ), esc_attr( $type ), esc_attr( $val ), 'color' === $type ? 'width:80px;height:36px' : 'width:100%' );
				}
			}
		},
		'urapress_ad',
		'normal',
		'high'
	);
}
add_action( 'add_meta_boxes', 'urapress_ad_metabox' );

function urapress_ad_save( $post_id ) {
	if ( ! isset( $_POST['urapress_ad_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['urapress_ad_nonce'] ) ), 'urapress_ad_save' ) ) {
		return;
	}
	if ( ! current_user_can( 'edit_post', $post_id ) ) {
		return;
	}
	foreach ( array_keys( urapress_ad_fields() ) as $key ) {
		$raw = wp_unslash( $_POST[ 'up_ad_' . $key ] ?? '' );
		$val = match ( $key ) {
			'url'    => esc_url_raw( $raw ),
			'accent' => sanitize_hex_color( $raw ) ?: '#D7141A',
			'text'   => sanitize_textarea_field( $raw ),
			default  => sanitize_text_field( $raw ),
		};
		update_post_meta( $post_id, '_up_ad_' . $key, $val );
	}
}
add_action( 'save_post_urapress_ad', 'urapress_ad_save' );

/* Spalte mit Bild in der Liste der Anzeigen. */
add_filter( 'manage_urapress_ad_posts_columns', fn( $c ) => array_merge( array_slice( $c, 0, 1 ), array( 'up_img' => 'Bild' ), array_slice( $c, 1 ) ) );
add_action(
	'manage_urapress_ad_posts_custom_column',
	function ( $col, $id ) {
		if ( 'up_img' === $col ) {
			echo get_the_post_thumbnail( $id, array( 80, 45 ) ); // phpcs:ignore
		}
	},
	10,
	2
);

/* Einmalig: die Startanzeigen als bearbeitbare Einträge anlegen (mit Bild). */
function urapress_seed_ads() {
	if ( get_option( 'urapress_ads_seeded' ) || ! current_user_can( 'manage_options' ) ) {
		return;
	}
	update_option( 'urapress_ads_seeded', 1 );
	require_once ABSPATH . 'wp-admin/includes/image.php';
	require_once ABSPATH . 'wp-admin/includes/file.php';
	require_once ABSPATH . 'wp-admin/includes/media.php';
	foreach ( urapress_default_ads() as $ad ) {
		$id = wp_insert_post(
			array(
				'post_type'   => 'urapress_ad',
				'post_status' => 'publish',
				'post_title'  => $ad['title'],
			)
		);
		if ( ! $id || is_wp_error( $id ) ) {
			continue;
		}
		foreach ( array_keys( urapress_ad_fields() ) as $key ) {
			update_post_meta( $id, '_up_ad_' . $key, $ad[ $key ] );
		}
		$file = get_template_directory() . '/assets/ads/' . $ad['id'] . '.jpg';
		if ( file_exists( $file ) ) {
			$tmp = wp_tempnam( $ad['id'] . '.jpg' );
			copy( $file, $tmp );
			$att = media_handle_sideload( array( 'name' => 'reklame-' . $ad['id'] . '.jpg', 'tmp_name' => $tmp ), $id );
			if ( ! is_wp_error( $att ) ) {
				set_post_thumbnail( $id, $att );
			}
		}
	}
}
add_action( 'admin_init', 'urapress_seed_ads' );

/** Alle aktiven Anzeigen: aus WordPress, sonst die Startanzeigen des Themes. */
function urapress_house_ads() {
	static $ads = null;
	if ( null !== $ads ) {
		return $ads;
	}
	$posts = get_posts(
		array(
			'post_type'      => 'urapress_ad',
			'post_status'    => 'publish',
			'posts_per_page' => 30,
		)
	);
	$ads = array();
	foreach ( $posts as $p ) {
		$ad = array(
			'id'    => 'ad' . $p->ID,
			'title' => get_the_title( $p ),
			'image' => get_the_post_thumbnail_url( $p, 'urapress-card' ),
		);
		foreach ( array_keys( urapress_ad_fields() ) as $key ) {
			$ad[ $key ] = get_post_meta( $p->ID, '_up_ad_' . $key, true );
		}
		if ( $ad['url'] ) {
			$ads[] = $ad;
		}
	}
	if ( ! $ads && ! get_option( 'urapress_ads_seeded' ) ) {
		foreach ( urapress_default_ads() as $ad ) {
			$file       = '/assets/ads/' . $ad['id'] . '.jpg';
			$ad['image'] = file_exists( get_template_directory() . $file ) ? get_template_directory_uri() . $file : '';
			$ads[]      = $ad;
		}
	}
	return $ads;
}

/** Kthen $count reklama në radhë të rastësishme (pa përsëritje brenda faqes). */
/** Eine bestimmte Anzeige anhand eines Textes in der URL holen (z. B. "tiffcore.ch"). */
function urapress_ad_by_url( $needle ) {
	foreach ( urapress_house_ads() as $ad ) {
		if ( ! empty( $ad['url'] ) && false !== stripos( $ad['url'], $needle ) ) {
			return $ad;
		}
	}
	return null;
}

function urapress_pick_ads( $count = 1 ) {
	static $used = array();
	$all = urapress_house_ads();
	if ( ! $all ) {
		return array();
	}
	$count = min( $count, count( $all ) );
	$ads   = array_filter( $all, fn( $a ) => ! in_array( $a['id'], $used, true ) );
	if ( count( $ads ) < $count ) {
		$used = array();
		$ads  = $all;
	}
	shuffle( $ads );
	$picked = array_slice( $ads, 0, $count );
	foreach ( $picked as $a ) {
		$used[] = $a['id'];
	}
	return $picked;
}

/** Shfaq një reklamë. $layout: card | wide */
function urapress_render_ad( $ad, $layout = 'card' ) {
	$url = add_query_arg(
		array(
			'utm_source'   => 'urapress',
			'utm_medium'   => 'banner',
			'utm_campaign' => $ad['id'],
		),
		$ad['url']
	);
	// TiffCore/Tiff: leuchtendes Logo als Animation (Canvas) statt Standbild.
	$host = (string) wp_parse_url( $ad['url'], PHP_URL_HOST );
	$glow = (bool) preg_match( '~(^|\.)(tiffcore\.ch|tiff-software-solutions\.com)$~i', $host );
	if ( $glow ) {
		wp_enqueue_script( 'urapress-glow', get_template_directory_uri() . '/assets/ads/glow.js', array(), URAPRESS_VERSION, true );
		$visual = sprintf( '<a class="up-hads__img up-hads__img--glow" href="%s" target="_blank" rel="sponsored noopener" tabindex="-1" aria-hidden="true"><canvas class="up-hads__glow" aria-hidden="true"></canvas></a>', esc_url( $url ) );
	} elseif ( ! empty( $ad['image'] ) ) {
		$visual = sprintf( '<a class="up-hads__img" href="%s" target="_blank" rel="sponsored noopener" tabindex="-1" aria-hidden="true"><img src="%s" alt="" loading="lazy"></a>', esc_url( $url ), esc_url( $ad['image'] ) );
	} else {
		$visual = '';
	}
	printf(
		'<aside class="up-hads up-hads--%1$s%9$s" style="--ad:%2$s">' .
		'%10$s' .
		'<div class="up-hads__body">' .
		'<span class="up-hads__label">%3$s</span>' .
		'<span class="up-hads__kicker">%4$s</span>' .
		'<strong class="up-hads__title">%5$s</strong>' .
		'<span class="up-hads__text">%6$s</span>' .
		'<a class="up-hads__cta" href="%7$s" target="_blank" rel="sponsored noopener">%8$s →</a>' .
		'</div></aside>',
		esc_attr( $layout ),
		esc_attr( $ad['accent'] ),
		esc_html__( 'Reklamë', 'urapress' ),
		esc_html( $ad['kicker'] ),
		esc_html( $ad['title'] ),
		esc_html( $ad['text'] ),
		esc_url( $url ),
		esc_html( $ad['cta'] ),
		'' === $visual ? '' : ' has-img',
		$visual
	);
}

/* Skripti për "Përgjigju" në komente. */
function urapress_comment_reply_script() {
	if ( is_singular() && comments_open() && get_option( 'thread_comments' ) ) {
		wp_enqueue_script( 'comment-reply' );
	}
}
add_action( 'wp_enqueue_scripts', 'urapress_comment_reply_script' );

/* Fusha "Website" hiqet nga formulari i komenteve (më pak spam). */
add_filter(
	'comment_form_default_fields',
	function ( $fields ) {
		unset( $fields['url'] );
		return $fields;
	}
);
