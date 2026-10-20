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
	foreach ( array( 'lloji', 'kategoria', 'vendi', 'telefoni', 'emri' ) as $k ) {
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
	?>
	<article class="up-nj up-nj--<?php echo esc_attr( $lloji ); ?>">
		<div class="up-nj__top">
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
