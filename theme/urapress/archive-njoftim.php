<?php
/**
 * Njoftime – Liste, Filter und Formular.
 *
 * @package UraPress
 */

get_header();
$urapress_base  = get_post_type_archive_link( 'njoftim' );
$urapress_lloji = isset( $_GET['lloji'] ) ? sanitize_key( wp_unslash( $_GET['lloji'] ) ) : '';
$urapress_kat   = isset( $_GET['kategoria'] ) ? sanitize_key( wp_unslash( $_GET['kategoria'] ) ) : '';
$urapress_msg   = isset( $_GET['nj'] ) ? sanitize_key( wp_unslash( $_GET['nj'] ) ) : '';
$urapress_msgs  = array(
	'ok'     => array( 'ok', 'Faleminderit! Njoftimi juaj u dërgua. Del në faqe pasi ta kontrollojë redaksia – zakonisht brenda një dite.' ),
	'mungon' => array( 'err', 'Diçka mungon: plotësoni titullin, tekstin, telefonin dhe pranoni kushtet.' ),
	'shume'  => array( 'err', 'Keni dërguar shumë njoftime brenda një ore. Provoni përsëri më vonë.' ),
	'gabim'  => array( 'err', 'Ndodhi një gabim. Ju lutemi provoni përsëri.' ),
);
$urapress_chip = function ( $label, $args, $active ) use ( $urapress_base ) {
	printf( '<a class="up-chip%s" href="%s">%s</a>', $active ? ' is-active' : '', esc_url( add_query_arg( $args, $urapress_base ) ), esc_html( $label ) );
};
?>
<main class="up-wrap up-njs">
	<header class="up-njs__head">
		<div>
			<h1 class="up-njs__title">Njoftime</h1>
			<p class="up-njs__sub">Kërkoni ose ofroni diçka brenda komunitetit – punë, zanatçi, banesë, veturë, shërbime. Falas.</p>
		</div>
		<a class="up-btn up-njs__add" href="#shto">+ Shto njoftim</a>
	</header>

	<nav class="up-njs__filters" aria-label="Filtro">
		<?php
		$urapress_chip( 'Të gjitha', array( 'kategoria' => $urapress_kat ?: false ), '' === $urapress_lloji );
		foreach ( urapress_nj_types() as $k => $v ) {
			$urapress_chip( $v, array( 'lloji' => $k, 'kategoria' => $urapress_kat ?: false ), $k === $urapress_lloji );
		}
		?>
		<span class="up-njs__sep"></span>
		<?php
		$urapress_chip( 'Çdo kategori', array( 'lloji' => $urapress_lloji ?: false ), '' === $urapress_kat );
		foreach ( urapress_nj_cats() as $k => $v ) {
			$urapress_chip( $v, array( 'kategoria' => $k, 'lloji' => $urapress_lloji ?: false ), $k === $urapress_kat );
		}
		?>
	</nav>

	<?php if ( have_posts() ) : ?>
		<div class="up-njs__grid">
			<?php
			while ( have_posts() ) :
				the_post();
				urapress_nj_card( get_post() );
			endwhile;
			?>
		</div>
		<?php the_posts_pagination( array( 'mid_size' => 1 ) ); ?>
	<?php else : ?>
		<p class="up-njs__empty">Ende nuk ka njoftime këtu. Bëhuni i pari – <a href="#shto">shtoni një njoftim</a>.</p>
	<?php endif; ?>

	<section class="up-njs__form" id="shto">
		<h2>Shto njoftim falas</h2>
		<p class="up-njs__note">Njoftimi del pas kontrollit nga redaksia dhe qëndron <?php echo (int) URAPRESS_NJ_DAYS; ?> ditë. Numri juaj i telefonit shfaqet në njoftim që të mund t'ju kontaktojnë.</p>
		<?php if ( isset( $urapress_msgs[ $urapress_msg ] ) ) : ?>
			<p class="up-njs__msg up-njs__msg--<?php echo esc_attr( $urapress_msgs[ $urapress_msg ][0] ); ?>"><?php echo esc_html( $urapress_msgs[ $urapress_msg ][1] ); ?></p>
		<?php endif; ?>
		<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>">
			<input type="hidden" name="action" value="urapress_nj">
			<?php wp_nonce_field( 'urapress_nj', 'nj_nonce' ); ?>
			<div class="up-njs__hp" aria-hidden="true"><label>Website <input type="text" name="nj_web" tabindex="-1" autocomplete="off"></label></div>
			<fieldset class="up-njs__lloji">
				<?php foreach ( urapress_nj_types() as $k => $v ) : ?>
					<label><input type="radio" name="nj_lloji" value="<?php echo esc_attr( $k ); ?>" <?php checked( 'kerkoj', $k ); ?> required> <?php echo esc_html( $v ); ?></label>
				<?php endforeach; ?>
			</fieldset>
			<div class="up-njs__row">
				<label>Kategoria
					<select name="nj_kategoria" required>
						<?php foreach ( urapress_nj_cats() as $k => $v ) : ?>
							<option value="<?php echo esc_attr( $k ); ?>"><?php echo esc_html( $v ); ?></option>
						<?php endforeach; ?>
					</select>
				</label>
				<label>Vendi <input type="text" name="nj_vendi" maxlength="40" placeholder="p.sh. Bern"></label>
			</div>
			<label>Titulli <input type="text" name="nj_titulli" minlength="5" maxlength="80" required placeholder="p.sh. Kërkoj pllakashtrues për 2 ditë punë (banjo)"></label>
			<label>Teksti <textarea name="nj_teksti" rows="5" minlength="10" maxlength="600" required placeholder="Përshkruani shkurt: çfarë, kur, ku…"></textarea></label>
			<div class="up-njs__row">
				<label>Emri <input type="text" name="nj_emri" maxlength="40" placeholder="p.sh. Arben"></label>
				<label>Telefoni / WhatsApp <input type="tel" name="nj_telefoni" required placeholder="079 123 45 67"></label>
			</div>
			<label class="up-njs__check"><input type="checkbox" name="nj_pranoj" value="1" required> Pranoj që numri im të publikohet në njoftim dhe që redaksia mund ta refuzojë njoftimin.</label>
			<button class="up-btn" type="submit">Dërgo njoftimin</button>
		</form>
	</section>
</main>
<?php
get_footer();
