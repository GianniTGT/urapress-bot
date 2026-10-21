<?php
/**
 * Hyr – Anmelden mit E-Mail-Code.
 *
 * @package UraPress
 */

$urapress_back  = isset( $_GET['kthehu'] ) ? wp_validate_redirect( esc_url_raw( wp_unslash( $_GET['kthehu'] ) ), home_url( '/' ) ) : home_url( '/' );
$urapress_token = isset( $_GET['t'] ) ? sanitize_key( wp_unslash( $_GET['t'] ) ) : '';
$urapress_err   = isset( $_GET['gabim'] ) ? sanitize_key( wp_unslash( $_GET['gabim'] ) ) : '';
$urapress_errs  = array(
	'email'   => 'Shkruani një adresë emaili të saktë.',
	'kodi'    => 'Kodi nuk është i saktë. Provoni përsëri.',
	'skadoi'  => 'Kodi ka skaduar. Kërkoni një kod të ri.',
	'shume'   => 'Shumë përpjekje. Provoni përsëri pas një ore.',
	'mail'    => 'Emaili nuk u dërgua. Provoni përsëri më vonë.',
	'sesioni' => 'Diçka shkoi keq. Provoni përsëri.',
);
$urapress_step2 = $urapress_token && get_transient( 'urapress_hyr_t_' . $urapress_token );

get_header();
?>
<main class="up-wrap up-hyr">
	<div class="up-hyr__box">
		<?php if ( is_user_logged_in() ) : ?>
			<h1>Je i kyçur ✔</h1>
			<p class="up-hyr__sub">Si <b><?php echo esc_html( wp_get_current_user()->user_email ); ?></b>. Tani i sheh të gjithë numrat te njoftimet.</p>
			<a class="up-btn" href="<?php echo esc_url( $urapress_back ); ?>">Vazhdo</a>
			<p class="up-hyr__small"><a href="<?php echo esc_url( wp_logout_url( home_url( '/' ) ) ); ?>">Dil nga llogaria</a></p>
		<?php else : ?>
			<h1><?php echo $urapress_step2 ? 'Shkruaj kodin' : 'Hyr në UraPress'; ?></h1>
			<p class="up-hyr__sub">
				<?php
				echo $urapress_step2
					? 'Të dërguam një kod me 6 shifra në email. Shiko edhe te «Spam».'
					: 'Pa fjalëkalim: shkruaj emailin, të dërgojmë një kod. Llogaria krijohet automatikisht – falas.';
				?>
			</p>
			<?php if ( isset( $urapress_errs[ $urapress_err ] ) ) : ?>
				<p class="up-njs__msg up-njs__msg--err"><?php echo esc_html( $urapress_errs[ $urapress_err ] ); ?></p>
			<?php endif; ?>
			<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
				<?php wp_nonce_field( 'urapress_hyr', 'hyr_nonce' ); ?>
				<input type="hidden" name="kthehu" value="<?php echo esc_url( $urapress_back ); ?>">
				<?php if ( $urapress_step2 ) : ?>
					<input type="hidden" name="action" value="urapress_hyr_verifiko">
					<input type="hidden" name="t" value="<?php echo esc_attr( $urapress_token ); ?>">
					<label>Kodi <input class="up-hyr__code" type="text" name="kodi" inputmode="numeric" autocomplete="one-time-code" maxlength="6" pattern="[0-9]{6}" required autofocus placeholder="••••••"></label>
					<button class="up-btn" type="submit">Hyr</button>
					<p class="up-hyr__small"><a href="<?php echo esc_url( add_query_arg( 'kthehu', rawurlencode( $urapress_back ), home_url( '/hyr/' ) ) ); ?>">Kërko një kod të ri</a></p>
				<?php else : ?>
					<input type="hidden" name="action" value="urapress_hyr_kod">
					<div class="up-njs__hp" aria-hidden="true"><label>Web <input type="text" name="hyr_web" tabindex="-1" autocomplete="off"></label></div>
					<label>Emaili <input type="email" name="email" autocomplete="email" required autofocus placeholder="emri@shembull.ch"></label>
					<button class="up-btn" type="submit">Më dërgo kodin</button>
					<p class="up-hyr__small">Emailin e përdorim vetëm për kyçje. Nuk e shfaqim askund.</p>
				<?php endif; ?>
			</form>
		<?php endif; ?>
	</div>
</main>
<?php
get_footer();
