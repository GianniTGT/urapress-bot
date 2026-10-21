<?php
/**
 * Llogaria – Anmelden ohne Passwort: E-Mail eingeben, 6-stelligen Code erhalten, fertig.
 * Wer neu ist, bekommt automatisch ein Konto (Rolle «subscriber», kein Zugang zum Backend).
 * Zweck: Anzeigen-Nummern sehen, die der Verkäufer nur für Angemeldete freigibt.
 *
 * @package UraPress
 */

const URAPRESS_HYR_MIN = 15; // Code gültig (Minuten)

/* Adresse /hyr/ */
add_action(
	'init',
	function () {
		add_rewrite_rule( '^hyr/?$', 'index.php?urapress_hyr=1', 'top' );
		if ( '1' !== get_option( 'urapress_hyr_flushed' ) ) {
			flush_rewrite_rules( false );
			update_option( 'urapress_hyr_flushed', '1' );
		}
	}
);
add_filter( 'query_vars', fn( $v ) => array_merge( $v, array( 'urapress_hyr' ) ) );
add_filter(
	'template_include',
	fn( $t ) => get_query_var( 'urapress_hyr' ) ? get_template_directory() . '/template-hyr.php' : $t
);

/* /hyr/ nicht in Google */
add_filter( 'wp_robots', fn( $r ) => get_query_var( 'urapress_hyr' ) ? array( 'noindex' => true, 'nofollow' => true ) : $r );
add_filter( 'pre_get_document_title', fn( $t ) => get_query_var( 'urapress_hyr' ) ? 'Hyr – UraPress' : $t );

/* Link zur Anmeldung, danach zurück zu $back */
function urapress_hyr_url( $back = '' ) {
	return add_query_arg( 'kthehu', rawurlencode( $back ?: home_url( add_query_arg( array() ) ) ), home_url( '/hyr/' ) );
}

/* E-Mails kommen von redaksia@urapress.ch */
add_filter( 'wp_mail_from', fn() => 'redaksia@urapress.ch' );
add_filter( 'wp_mail_from_name', fn() => 'UraPress' );

/* Angemeldete Leser: keine Admin-Leiste, kein Backend */
add_filter( 'show_admin_bar', fn( $show ) => current_user_can( 'edit_posts' ) ? $show : false );
add_action(
	'admin_init',
	function () {
		if ( ! current_user_can( 'edit_posts' ) && ! wp_doing_ajax() && 'admin-post.php' !== basename( $_SERVER['SCRIPT_NAME'] ?? '' ) ) { // phpcs:ignore
			wp_safe_redirect( home_url( '/' ) );
			exit;
		}
	}
);

function urapress_hyr_ip_key( $what ) {
	return 'urapress_hyr_' . $what . '_' . md5( isset( $_SERVER['REMOTE_ADDR'] ) ? sanitize_text_field( wp_unslash( $_SERVER['REMOTE_ADDR'] ) ) : '' );
}

/* Schritt 1: E-Mail → Code schicken */
function urapress_hyr_send_code() {
	$back = isset( $_POST['kthehu'] ) ? wp_validate_redirect( esc_url_raw( wp_unslash( $_POST['kthehu'] ) ), home_url( '/' ) ) : home_url( '/' );
	$go   = function ( $args ) use ( $back ) {
		wp_safe_redirect( add_query_arg( $args + array( 'kthehu' => rawurlencode( $back ) ), home_url( '/hyr/' ) ) );
		exit;
	};
	if ( ! isset( $_POST['hyr_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['hyr_nonce'] ) ), 'urapress_hyr' ) ) {
		$go( array( 'gabim' => 'sesioni' ) );
	}
	if ( ! empty( $_POST['hyr_web'] ) ) { // unsichtbares Feld: nur Bots
		$go( array( 'gabim' => 'sesioni' ) );
	}
	$email = sanitize_email( wp_unslash( $_POST['email'] ?? '' ) );
	if ( ! is_email( $email ) ) {
		$go( array( 'gabim' => 'email' ) );
	}
	$ipk = urapress_hyr_ip_key( 'send' );
	$n   = (int) get_transient( $ipk );
	if ( $n >= 6 ) {
		$go( array( 'gabim' => 'shume' ) );
	}
	set_transient( $ipk, $n + 1, HOUR_IN_SECONDS );

	$code  = (string) wp_rand( 100000, 999999 );
	$token = strtolower( wp_generate_password( 20, false ) );
	set_transient(
		'urapress_hyr_t_' . $token,
		array( 'email' => strtolower( $email ), 'hash' => wp_hash_password( $code ), 'tries' => 0 ),
		URAPRESS_HYR_MIN * MINUTE_IN_SECONDS
	);
	$sent = wp_mail(
		$email,
		'Kodi yt për UraPress: ' . $code,
		"Përshëndetje!\n\nKodi yt për t'u kyçur në UraPress është:\n\n    " . $code . "\n\nKodi vlen " . URAPRESS_HYR_MIN . " minuta. Nëse nuk e ke kërkuar ti, injoroje këtë email.\n\nUraPress – Ura mes Atdheut dhe Dijasporës\nhttps://urapress.ch"
	);
	if ( ! $sent ) {
		$go( array( 'gabim' => 'mail' ) );
	}
	$go( array( 't' => $token ) );
}
add_action( 'admin_post_nopriv_urapress_hyr_kod', 'urapress_hyr_send_code' );
add_action( 'admin_post_urapress_hyr_kod', 'urapress_hyr_send_code' );

/* Schritt 2: Code prüfen → anmelden (Konto wird bei Bedarf erstellt) */
function urapress_hyr_verify() {
	$back  = isset( $_POST['kthehu'] ) ? wp_validate_redirect( esc_url_raw( wp_unslash( $_POST['kthehu'] ) ), home_url( '/' ) ) : home_url( '/' );
	$token = sanitize_key( wp_unslash( $_POST['t'] ?? '' ) );
	$code  = preg_replace( '/\D/', '', wp_unslash( $_POST['kodi'] ?? '' ) ); // phpcs:ignore
	$back_to_form = function ( $err ) use ( $token, $back ) {
		wp_safe_redirect( add_query_arg( array( 't' => $token, 'gabim' => $err, 'kthehu' => rawurlencode( $back ) ), home_url( '/hyr/' ) ) );
		exit;
	};
	if ( ! isset( $_POST['hyr_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['hyr_nonce'] ) ), 'urapress_hyr' ) ) {
		$back_to_form( 'sesioni' );
	}
	$key  = 'urapress_hyr_t_' . $token;
	$data = $token ? get_transient( $key ) : false;
	if ( ! $data ) {
		wp_safe_redirect( add_query_arg( array( 'gabim' => 'skadoi', 'kthehu' => rawurlencode( $back ) ), home_url( '/hyr/' ) ) );
		exit;
	}
	if ( ! wp_check_password( $code, $data['hash'] ) ) {
		++$data['tries'];
		if ( $data['tries'] >= 5 ) {
			delete_transient( $key );
			wp_safe_redirect( add_query_arg( array( 'gabim' => 'skadoi', 'kthehu' => rawurlencode( $back ) ), home_url( '/hyr/' ) ) );
			exit;
		}
		set_transient( $key, $data, URAPRESS_HYR_MIN * MINUTE_IN_SECONDS );
		$back_to_form( 'kodi' );
	}
	delete_transient( $key );

	$user = get_user_by( 'email', $data['email'] );
	if ( ! $user ) {
		$id = wp_insert_user(
			array(
				'user_login'   => 'lexues_' . strtolower( wp_generate_password( 10, false ) ),
				'user_email'   => $data['email'],
				'user_pass'    => wp_generate_password( 32 ),
				'display_name' => ucfirst( strtok( $data['email'], '@' ) ),
				'role'         => 'subscriber',
			)
		);
		if ( is_wp_error( $id ) ) {
			$back_to_form( 'sesioni' );
		}
		$user = get_user_by( 'id', $id );
	}
	wp_set_current_user( $user->ID );
	wp_set_auth_cookie( $user->ID, true, is_ssl() );
	wp_safe_redirect( add_query_arg( 'hyre', '1', $back ) );
	exit;
}
add_action( 'admin_post_nopriv_urapress_hyr_verifiko', 'urapress_hyr_verify' );
add_action( 'admin_post_urapress_hyr_verifiko', 'urapress_hyr_verify' );
