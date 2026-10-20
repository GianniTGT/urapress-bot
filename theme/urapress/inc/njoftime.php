<?php
/**
 * Njoftime – kleine Anzeigen (Kërkoj / Ofroj).
 * Besucher schicken das Formular, die Anzeige wartet als "pending",
 * der Telegram-Bot meldet sie der Redaktion und gibt sie frei (✅) oder löscht sie (❌).
 *
 * @package UraPress
 */

const URAPRESS_NJ_DAYS = 30;

function urapress_nj_types() {
	return array( 'kerkoj' => 'Kërkoj', 'ofroj' => 'Ofroj' );
}

function urapress_nj_cats() {
	return array(
		'pune'     => 'Punë & zanate',
		'banese'   => 'Banesë',
		'vetura'   => 'Vetura',
		'sherbime' => 'Shërbime',
		'shitje'   => 'Shitje & blerje',
		'tjera'    => 'Të tjera',
	);
}

function urapress_nj_register() {
	register_post_type(
		'njoftim',
		array(
			'labels'       => array( 'name' => 'Njoftime', 'singular_name' => 'Njoftim', 'menu_name' => 'Njoftime' ),
			'public'       => true,
			'has_archive'  => 'njoftime',
			'rewrite'      => array( 'slug' => 'njoftim', 'with_front' => false ),
			'supports'     => array( 'title', 'editor' ),
			'menu_icon'    => 'dashicons-megaphone',
			'show_in_rest' => true,
			'rest_base'    => 'njoftime',
		)
	);
	foreach ( array( 'lloji', 'kategoria', 'vendi', 'telefoni', 'emri', 'theksuar' ) as $k ) {
		register_post_meta(
			'njoftim',
			'_nj_' . $k,
			array(
				'type'          => 'string',
				'single'        => true,
				'show_in_rest'  => true,
				'auth_callback' => fn() => current_user_can( 'edit_posts' ),
			)
		);
	}
}
add_action( 'init', 'urapress_nj_register' );

/* Einmalig die Adressen /njoftime/ und /njoftim/... aktivieren. */
function urapress_nj_flush() {
	if ( '1' !== get_option( 'urapress_nj_flushed' ) ) {
		flush_rewrite_rules( false );
		update_option( 'urapress_nj_flushed', '1' );
	}
}
add_action( 'init', 'urapress_nj_flush', 20 );

/* Liste: nur die letzten 30 Tage, Filter über ?lloji= und ?kategoria= */
function urapress_nj_query( $q ) {
	if ( is_admin() || ! $q->is_main_query() || ! $q->is_post_type_archive( 'njoftim' ) ) {
		return;
	}
	$q->set( 'posts_per_page', 24 );
	$q->set( 'date_query', array( array( 'after' => URAPRESS_NJ_DAYS . ' days ago' ) ) );
	$kerko = isset( $_GET['q'] ) ? sanitize_text_field( wp_unslash( $_GET['q'] ) ) : '';
	if ( '' !== $kerko ) {
		$q->set( 's', $kerko );
	}
	$q->set( 'post__not_in', urapress_nj_highlighted_ids() ); // die hervorgehobenen stehen oben extra
	$meta  = array();
	$lloji = isset( $_GET['lloji'] ) ? sanitize_key( wp_unslash( $_GET['lloji'] ) ) : '';
	$kat   = isset( $_GET['kategoria'] ) ? sanitize_key( wp_unslash( $_GET['kategoria'] ) ) : '';
	if ( isset( urapress_nj_types()[ $lloji ] ) ) {
		$meta[] = array( 'key' => '_nj_lloji', 'value' => $lloji );
	}
	if ( isset( urapress_nj_cats()[ $kat ] ) ) {
		$meta[] = array( 'key' => '_nj_kategoria', 'value' => $kat );
	}
	if ( $meta ) {
		$q->set( 'meta_query', $meta );
	}
}
add_action( 'pre_get_posts', 'urapress_nj_query' );

/* Hervorgehobene Anzeigen (bezahlt): _nj_theksuar = Zeitpunkt, bis wann */
function urapress_nj_is_highlighted( $id ) {
	return (int) get_post_meta( $id, '_nj_theksuar', true ) > time();
}

function urapress_nj_highlighted_ids() {
	static $ids = null;
	if ( null === $ids ) {
		$ids = get_posts(
			array(
				'post_type'      => 'njoftim',
				'post_status'    => 'publish',
				'posts_per_page' => 50,
				'fields'         => 'ids',
				'meta_query'     => array( array( 'key' => '_nj_theksuar', 'value' => time(), 'compare' => '>', 'type' => 'NUMERIC' ) ),
			)
		);
	}
	return $ids;
}

/* Anzahl aktiver Anzeigen pro Kategorie (optional nur Kërkoj oder Ofroj) */
function urapress_nj_counts( $lloji = '' ) {
	$args = array(
		'post_type'      => 'njoftim',
		'post_status'    => 'publish',
		'posts_per_page' => 1000,
		'fields'         => 'ids',
		'date_query'     => array( array( 'after' => URAPRESS_NJ_DAYS . ' days ago' ) ),
	);
	if ( isset( urapress_nj_types()[ $lloji ] ) ) {
		$args['meta_query'] = array( array( 'key' => '_nj_lloji', 'value' => $lloji ) );
	}
	$counts = array_fill_keys( array_keys( urapress_nj_cats() ), 0 );
	foreach ( get_posts( $args ) as $id ) {
		$k = get_post_meta( $id, '_nj_kategoria', true );
		if ( isset( $counts[ $k ] ) ) {
			++$counts[ $k ];
		}
	}
	return $counts;
}

/* Eigene Bildchen für die Kategorie-Kacheln: [Hintergrund, SVG] */
function urapress_nj_icon( $k ) {
	$i = array(
		'pune'     => array( '#FDE7D3', '<g transform="rotate(-35 60 64)"><rect x="54" y="38" width="12" height="70" rx="5" fill="#B5762E"/><rect x="30" y="22" width="60" height="24" rx="7" fill="#5C6B7A"/><rect x="30" y="22" width="14" height="24" rx="5" fill="#46525E"/></g>' ),
		'banese'   => array( '#E3E9F8', '<path d="M20 58 L60 24 L100 58 V100 H20Z" fill="#2346A0"/><path d="M12 60 L60 18 L108 60" fill="none" stroke="#D7141A" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/><rect x="50" y="70" width="20" height="30" rx="3" fill="#F3C76B"/><rect x="30" y="64" width="14" height="14" rx="2" fill="#BFD3FF"/><rect x="76" y="64" width="14" height="14" rx="2" fill="#BFD3FF"/>' ),
		'vetura'   => array( '#FBE0E1', '<path d="M14 74 Q16 58 30 56 L40 40 Q44 34 52 34 H76 Q84 34 88 40 L98 56 Q110 58 108 74 V84 H14Z" fill="#D7141A"/><path d="M44 42 H60 V56 H36Z M66 42 H80 L88 56 H66Z" fill="#CFE4F5"/><circle cx="36" cy="86" r="12" fill="#16181D"/><circle cx="36" cy="86" r="5" fill="#C9CCD3"/><circle cx="86" cy="86" r="12" fill="#16181D"/><circle cx="86" cy="86" r="5" fill="#C9CCD3"/><rect x="98" y="64" width="8" height="6" rx="2" fill="#FFE27A"/>' ),
		'sherbime' => array( '#DDF1E8', '<path d="M18 64 L42 46 L60 56 L78 46 L102 64 L76 88 Q70 94 62 88 L18 64Z" fill="#F3CBAE" stroke="#B9876A" stroke-width="3" stroke-linejoin="round"/><path d="M10 60 L30 44 L42 52 L22 70Z" fill="#0E8A7E"/><path d="M110 60 L90 44 L78 52 L98 70Z" fill="#2E9E4F"/><path d="M50 72 L58 80 M58 66 L68 76 M66 62 L76 72" stroke="#B9876A" stroke-width="3" stroke-linecap="round"/>' ),
		'shitje'   => array( '#EFE5FA', '<path d="M28 36 H92 L84 102 H36Z" fill="#6A4FB3"/><path d="M44 46 V34 a16 16 0 0 1 32 0 V46" fill="none" stroke="#3E2C78" stroke-width="7" stroke-linecap="round"/><path d="M62 58 L90 58 L98 70 L90 82 L62 82Z" fill="#FFD400" transform="rotate(-14 80 70)"/><circle cx="70" cy="72" r="4" fill="#6A4FB3"/>' ),
		'tjera'    => array( '#F1F2F4', '<rect x="24" y="24" width="72" height="72" rx="20" fill="#16181D"/><circle cx="42" cy="60" r="7" fill="#fff"/><circle cx="60" cy="60" r="7" fill="#fff"/><circle cx="78" cy="60" r="7" fill="#fff"/>' ),
	);
	return $i[ $k ] ?? $i['tjera'];
}

/* Formular verarbeiten */
function urapress_nj_submit() {
	$back = get_post_type_archive_link( 'njoftim' );
	$go   = function ( $status ) use ( $back ) {
		wp_safe_redirect( add_query_arg( 'nj', $status, $back ) . '#shto' );
		exit;
	};
	if ( ! isset( $_POST['nj_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['nj_nonce'] ) ), 'urapress_nj' ) ) {
		$go( 'gabim' );
	}
	if ( ! empty( $_POST['nj_web'] ) ) { // unsichtbares Feld: nur Bots füllen es aus
		$go( 'ok' );
	}
	$ip_key = 'urapress_nj_' . md5( isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '' );
	$count  = (int) get_transient( $ip_key );
	if ( $count >= 3 ) {
		$go( 'shume' );
	}
	$f = function ( $k ) {
		return isset( $_POST[ $k ] ) ? wp_unslash( $_POST[ $k ] ) : ''; // phpcs:ignore
	};
	$lloji   = sanitize_key( $f( 'nj_lloji' ) );
	$kat     = sanitize_key( $f( 'nj_kategoria' ) );
	$titulli = sanitize_text_field( $f( 'nj_titulli' ) );
	$teksti  = sanitize_textarea_field( $f( 'nj_teksti' ) );
	$vendi   = sanitize_text_field( $f( 'nj_vendi' ) );
	$emri    = sanitize_text_field( $f( 'nj_emri' ) );
	$tel     = trim( preg_replace( '/[^0-9+ ]/', '', $f( 'nj_telefoni' ) ) );
	$ok      = isset( urapress_nj_types()[ $lloji ] ) && isset( urapress_nj_cats()[ $kat ] )
		&& mb_strlen( $titulli ) >= 5 && mb_strlen( $titulli ) <= 80
		&& mb_strlen( $teksti ) >= 10 && mb_strlen( $teksti ) <= 600
		&& mb_strlen( $vendi ) <= 40 && mb_strlen( $emri ) <= 40
		&& strlen( preg_replace( '/\D/', '', $tel ) ) >= 9
		&& ! empty( $_POST['nj_pranoj'] );
	if ( ! $ok ) {
		$go( 'mungon' );
	}
	$id = wp_insert_post(
		array(
			'post_type'    => 'njoftim',
			'post_status'  => 'pending',
			'post_title'   => $titulli,
			'post_content' => $teksti,
			'post_author'  => 0,
		)
	);
	if ( ! $id || is_wp_error( $id ) ) {
		$go( 'gabim' );
	}
	foreach ( array( 'lloji' => $lloji, 'kategoria' => $kat, 'vendi' => $vendi, 'telefoni' => $tel, 'emri' => $emri ) as $k => $v ) {
		update_post_meta( $id, '_nj_' . $k, $v );
	}
	set_transient( $ip_key, $count + 1, HOUR_IN_SECONDS );
	$go( 'ok' );
}
add_action( 'admin_post_nopriv_urapress_nj', 'urapress_nj_submit' );
add_action( 'admin_post_urapress_nj', 'urapress_nj_submit' );

/* Telefon-Links: anrufen und WhatsApp (Schweizer 0xx → 41xx) */
function urapress_nj_wa( $tel ) {
	$d = preg_replace( '/\D/', '', $tel );
	if ( str_starts_with( $tel, '+' ) ) {
		return $d;
	}
	if ( str_starts_with( $d, '00' ) ) {
		return substr( $d, 2 );
	}
	if ( str_starts_with( $d, '0' ) ) {
		return '41' . substr( $d, 1 );
	}
	return $d;
}

/* Eine Anzeige als Karte */
function urapress_nj_card( $post, $full = false ) {
	$m     = fn( $k ) => (string) get_post_meta( $post->ID, '_nj_' . $k, true );
	$lloji = $m( 'lloji' );
	$tel   = $m( 'telefoni' );
	$text  = $full ? $post->post_content : wp_trim_words( $post->post_content, 40, '…' );
	$star  = urapress_nj_is_highlighted( $post->ID );
	?>
	<article class="up-nj up-nj--<?php echo esc_attr( $lloji ); ?><?php echo $star ? ' up-nj--theksuar' : ''; ?>">
		<div class="up-nj__top">
			<?php if ( $star ) : ?><span class="up-nj__star">⭐ I theksuar</span><?php endif; ?>
			<span class="up-nj__lloji"><?php echo esc_html( urapress_nj_types()[ $lloji ] ?? '' ); ?></span>
			<span class="up-nj__kat"><?php echo esc_html( urapress_nj_cats()[ $m( 'kategoria' ) ] ?? '' ); ?></span>
			<?php if ( $m( 'vendi' ) ) : ?><span class="up-nj__vendi">📍 <?php echo esc_html( $m( 'vendi' ) ); ?></span><?php endif; ?>
		</div>
		<h3 class="up-nj__titulli"><a href="<?php echo esc_url( get_permalink( $post ) ); ?>"><?php echo esc_html( get_the_title( $post ) ); ?></a></h3>
		<p class="up-nj__teksti"><?php echo nl2br( esc_html( $text ) ); ?></p>
		<div class="up-nj__fund">
			<span class="up-nj__meta"><?php echo esc_html( trim( $m( 'emri' ) . ' · ' . human_time_diff( get_post_time( 'U', true, $post ) ) . ' më parë', ' ·' ) ); ?></span>
			<?php if ( $tel ) : ?>
				<a class="up-nj__btn" href="tel:<?php echo esc_attr( preg_replace( '/[^0-9+]/', '', $tel ) ); ?>">📞 <?php echo esc_html( $tel ); ?></a>
				<a class="up-nj__btn up-nj__btn--wa" href="https://wa.me/<?php echo esc_attr( urapress_nj_wa( $tel ) ); ?>" target="_blank" rel="noopener nofollow">WhatsApp</a>
			<?php endif; ?>
		</div>
	</article>
	<?php
}

/* "Njoftime" in der Rubriken-Leiste und im Footer-Menü */
function urapress_nj_footer_item( $items, $args ) {
	if ( isset( $args->theme_location ) && 'footer' === $args->theme_location ) {
		$items = sprintf( '<li><a href="%s">Njoftime</a></li>', esc_url( get_post_type_archive_link( 'njoftim' ) ) ) . $items;
	}
	return $items;
}
add_filter( 'wp_nav_menu_items', 'urapress_nj_footer_item', 10, 2 );
