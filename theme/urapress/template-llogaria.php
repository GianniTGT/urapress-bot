<?php
/**
 * Llogaria ime – eigene Anzeigen und gemerkte Anzeigen.
 *
 * @package UraPress
 */

$urapress_user = wp_get_current_user();
$urapress_msg  = isset( $_GET['msg'] ) ? sanitize_key( wp_unslash( $_GET['msg'] ) ) : '';
$urapress_msgs = array(
	'fshire'    => array( 'ok', 'Njoftimi u fshi.' ),
	'rinovuar'  => array( 'ok', 'Njoftimi u rinovua – qëndron edhe 30 ditë.' ),
	'ndryshuar' => array( 'ok', 'Ndryshimet u ruajtën. Njoftimi del përsëri pas kontrollit nga redaksia.' ),
	'ruajtur'   => array( 'ok', 'U ruajt.' ),
	'mungon'    => array( 'err', 'Diçka mungon: titulli, teksti, telefoni – te veturat edhe marka, modeli dhe çmimi.' ),
	'gabim'     => array( 'err', 'Ndodhi një gabim. Provoni përsëri.' ),
);
$urapress_edit = isset( $_GET['ndrysho'] ) ? get_post( absint( $_GET['ndrysho'] ) ) : null;
if ( $urapress_edit && ! urapress_nj_is_mine( $urapress_edit ) ) {
	$urapress_edit = null;
}
$urapress_mine = get_posts(
	array(
		'post_type'      => 'njoftim',
		'post_status'    => array( 'publish', 'pending' ),
		'author'         => $urapress_user->ID,
		'posts_per_page' => 50,
	)
);
$urapress_saved = urapress_saved_ids() ? get_posts(
	array(
		'post_type'      => 'njoftim',
		'post_status'    => 'publish',
		'post__in'       => urapress_saved_ids(),
		'posts_per_page' => 100,
		'orderby'        => 'post__in',
	)
) : array();
$urapress_action = function ( $post, $veprim, $label, $class = '', $confirm = '' ) {
	?>
	<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>"<?php echo $confirm ? ' onsubmit="return confirm(\'' . esc_js( $confirm ) . '\')"' : ''; ?>>
		<input type="hidden" name="action" value="urapress_llog">
		<input type="hidden" name="veprim" value="<?php echo esc_attr( $veprim ); ?>">
		<input type="hidden" name="id" value="<?php echo (int) $post->ID; ?>">
		<?php wp_nonce_field( 'urapress_llog_' . $post->ID, 'llog_nonce' ); ?>
		<button type="submit" class="up-llog__btn <?php echo esc_attr( $class ); ?>"><?php echo esc_html( $label ); ?></button>
	</form>
	<?php
};

get_header();
?>
<main class="up-wrap up-llog">
	<header class="up-llog__head">
		<div>
			<h1>Llogaria ime</h1>
			<p><?php echo esc_html( $urapress_user->user_email ); ?> · <a href="<?php echo esc_url( wp_logout_url( home_url( '/' ) ) ); ?>">Dil</a></p>
		</div>
		<a class="up-njhome__add" href="<?php echo esc_url( get_post_type_archive_link( 'njoftim' ) ); ?>#shto">+ Shto njoftim</a>
	</header>

	<?php if ( isset( $urapress_msgs[ $urapress_msg ] ) ) : ?>
		<p class="up-njs__msg up-njs__msg--<?php echo esc_attr( $urapress_msgs[ $urapress_msg ][0] ); ?>"><?php echo esc_html( $urapress_msgs[ $urapress_msg ][1] ); ?></p>
	<?php endif; ?>

	<?php
	if ( $urapress_edit ) :
		$m = fn( $k ) => (string) get_post_meta( $urapress_edit->ID, '_nj_' . $k, true );
		?>
		<section class="up-njs__form up-llog__edit">
			<h2>Ndrysho njoftimin</h2>
			<p class="up-njs__note">Pas ndryshimit njoftimi kontrollohet përsëri nga redaksia. Fotot mbeten si janë.</p>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<input type="hidden" name="action" value="urapress_llog">
				<input type="hidden" name="veprim" value="ndrysho">
				<input type="hidden" name="id" value="<?php echo (int) $urapress_edit->ID; ?>">
				<?php wp_nonce_field( 'urapress_llog_' . $urapress_edit->ID, 'llog_nonce' ); ?>
				<fieldset class="up-njs__lloji">
					<?php foreach ( urapress_nj_types() as $k => $v ) : ?>
						<label><input type="radio" name="nj_lloji" value="<?php echo esc_attr( $k ); ?>" <?php checked( $m( 'lloji' ), $k ); ?> required> <?php echo esc_html( $v ); ?></label>
					<?php endforeach; ?>
				</fieldset>
				<div class="up-njs__row">
					<label>Kategoria
						<select name="nj_kategoria" required>
							<?php foreach ( urapress_nj_cats() as $k => $v ) : ?>
								<option value="<?php echo esc_attr( $k ); ?>" <?php selected( $m( 'kategoria' ), $k ); ?>><?php echo esc_html( $v ); ?></option>
							<?php endforeach; ?>
						</select>
					</label>
					<label>Vendi <input type="text" name="nj_vendi" maxlength="40" value="<?php echo esc_attr( $m( 'vendi' ) ); ?>"></label>
				</div>
				<fieldset class="up-njs__car" data-nj-car>
					<legend>🚗 Vetëm te veturat</legend>
					<div class="up-njs__row3">
						<label>Marka <input type="text" name="nj_marka" maxlength="30" value="<?php echo esc_attr( $m( 'marka' ) ); ?>"></label>
						<label>Modeli <input type="text" name="nj_modeli" maxlength="40" value="<?php echo esc_attr( $m( 'modeli' ) ); ?>"></label>
						<label>Çmimi (CHF) <input type="text" name="nj_cmimi" inputmode="numeric" maxlength="9" value="<?php echo esc_attr( $m( 'cmimi' ) ); ?>"></label>
					</div>
				</fieldset>
				<label>Titulli <input type="text" name="nj_titulli" minlength="5" maxlength="80" required value="<?php echo esc_attr( $urapress_edit->post_title ); ?>"></label>
				<label>Teksti <textarea name="nj_teksti" rows="5" minlength="10" maxlength="600" required><?php echo esc_textarea( $urapress_edit->post_content ); ?></textarea></label>
				<div class="up-njs__row">
					<label>Emri <input type="text" name="nj_emri" maxlength="40" value="<?php echo esc_attr( $m( 'emri' ) ); ?>"></label>
					<label>Telefoni / WhatsApp <input type="tel" name="nj_telefoni" required value="<?php echo esc_attr( $m( 'telefoni' ) ); ?>"></label>
				</div>
				<fieldset class="up-njs__lloji up-njs__numri">
					<legend>Kush e sheh numrin tënd?</legend>
					<label><input type="radio" name="nj_numri" value="te_gjithe" <?php checked( 'anetaret' !== $m( 'numri' ) ); ?>> Të gjithë</label>
					<label><input type="radio" name="nj_numri" value="anetaret" <?php checked( 'anetaret', $m( 'numri' ) ); ?>> Vetëm anëtarët e kyçur 🔒</label>
				</fieldset>
				<fieldset class="up-njs__lloji up-njs__numri">
					<legend>Gjuha e njoftimit / Sprache der Anzeige</legend>
					<label><input type="radio" name="nj_gjuha" value="sq" <?php checked( 'de' !== $m( 'gjuha' ) ); ?>> Shqip</label>
					<label><input type="radio" name="nj_gjuha" value="de" <?php checked( 'de', $m( 'gjuha' ) ); ?>> Deutsch</label>
				</fieldset>
				<div class="up-llog__formbtns">
					<button class="up-btn" type="submit">Ruaj ndryshimet</button>
					<a href="<?php echo esc_url( home_url( '/llogaria/' ) ); ?>">Anulo</a>
				</div>
			</form>
		</section>
	<?php endif; ?>

	<section class="up-llog__sec">
		<h2>Njoftimet e mia</h2>
		<?php if ( ! $urapress_mine ) : ?>
			<p class="up-njs__empty">Nuk keni ende njoftime. <a href="<?php echo esc_url( get_post_type_archive_link( 'njoftim' ) ); ?>#shto">Shtoni njoftimin e parë</a> – falas.</p>
		<?php else : ?>
			<ul class="up-llog__list">
				<?php
				foreach ( $urapress_mine as $urapress_p ) :
					$urapress_age  = time() - get_post_time( 'U', true, $urapress_p );
					$urapress_left = (int) ceil( ( URAPRESS_NJ_DAYS * DAY_IN_SECONDS - $urapress_age ) / DAY_IN_SECONDS );
					if ( 'pending' === $urapress_p->post_status ) {
						$urapress_st = array( 'pritje', '⏳ Në kontroll' );
					} elseif ( $urapress_left <= 0 ) {
						$urapress_st = array( 'skaduar', 'Ka skaduar' );
					} else {
						$urapress_st = array( 'online', '✔ Online · edhe ' . $urapress_left . ' ditë' );
					}
					$urapress_foto = urapress_nj_photo_ids( $urapress_p->ID );
					?>
					<li class="up-llog__item">
						<span class="up-llog__thumb">
							<?php
							if ( $urapress_foto ) {
								echo wp_get_attachment_image( $urapress_foto[0], 'thumbnail' );
							} else {
								list( $urapress_bg, $urapress_svg ) = urapress_nj_icon( get_post_meta( $urapress_p->ID, '_nj_kategoria', true ) );
								printf( '<span style="background:%s"><svg viewBox="0 0 120 120">%s</svg></span>', esc_attr( $urapress_bg ), $urapress_svg ); // phpcs:ignore
							}
							?>
						</span>
						<div class="up-llog__info">
							<a href="<?php echo esc_url( get_permalink( $urapress_p ) ); ?>"><b><?php echo esc_html( get_the_title( $urapress_p ) ); ?></b></a>
							<span class="up-llog__st up-llog__st--<?php echo esc_attr( $urapress_st[0] ); ?>"><?php echo esc_html( $urapress_st[1] ); ?></span>
						</div>
						<div class="up-llog__acts">
							<a class="up-llog__btn" href="<?php echo esc_url( add_query_arg( 'ndrysho', $urapress_p->ID, home_url( '/llogaria/' ) ) ); ?>">✏️ Ndrysho</a>
							<?php
							if ( urapress_nj_can_renew( $urapress_p ) ) {
								$urapress_action( $urapress_p, 'rinovo', '🔄 Rinovo 30 ditë', 'is-main' );
							}
							$urapress_action( $urapress_p, 'fshi', '🗑 Fshi', 'is-del', 'Ta fshijmë njoftimin «' . get_the_title( $urapress_p ) . '»?' );
							?>
						</div>
					</li>
				<?php endforeach; ?>
			</ul>
		<?php endif; ?>
	</section>

	<section class="up-llog__sec">
		<h2>Të ruajturat ★</h2>
		<?php if ( ! $urapress_saved ) : ?>
			<p class="up-njs__empty">Asgjë e ruajtur. Te çdo njoftim shtypni <b>☆ Ruaje</b>.</p>
		<?php else : ?>
			<div class="up-njs__grid">
				<?php
				foreach ( $urapress_saved as $urapress_p ) {
					urapress_nj_card( $urapress_p );
				}
				?>
			</div>
		<?php endif; ?>
	</section>
</main>
<?php
get_footer();
