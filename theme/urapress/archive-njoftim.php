<?php
/**
 * Njoftime – Suche, Kategorie-Kacheln, Liste und Formular.
 *
 * @package UraPress
 */

get_header();
$urapress_base  = get_post_type_archive_link( 'njoftim' );
$urapress_lloji = isset( $_GET['lloji'] ) ? sanitize_key( wp_unslash( $_GET['lloji'] ) ) : '';
$urapress_kat   = isset( $_GET['kategoria'] ) ? sanitize_key( wp_unslash( $_GET['kategoria'] ) ) : '';
$urapress_q     = isset( $_GET['q'] ) ? sanitize_text_field( wp_unslash( $_GET['q'] ) ) : '';
$urapress_msg   = isset( $_GET['nj'] ) ? sanitize_key( wp_unslash( $_GET['nj'] ) ) : '';
$urapress_msgs  = array(
	'ok'     => array( 'ok', 'Faleminderit! Njoftimi juaj u dërgua. Del në faqe pasi ta kontrollojë redaksia – zakonisht brenda një dite.' ),
	'mungon' => array( 'err', 'Diçka mungon: plotësoni titullin, tekstin, telefonin dhe pranoni kushtet. Te veturat: marka, modeli dhe çmimi.' ),
	'shume'  => array( 'err', 'Keni dërguar shumë njoftime brenda një ore. Provoni përsëri më vonë.' ),
	'gabim'  => array( 'err', 'Ndodhi një gabim. Ju lutemi provoni përsëri.' ),
);
$urapress_counts   = urapress_nj_counts( $urapress_lloji );
$urapress_filtered = $urapress_kat || $urapress_q || $urapress_lloji;
$urapress_cats     = urapress_nj_cats();

/* Hervorgehobene Anzeigen passend zum Filter */
$urapress_star_args = array(
	'post_type'      => 'njoftim',
	'post__in'       => urapress_nj_highlighted_ids() ?: array( 0 ),
	'posts_per_page' => 6,
	'orderby'        => 'rand',
	's'              => $urapress_q,
	'meta_query'     => array_values(
		array_filter(
			array(
				isset( urapress_nj_types()[ $urapress_lloji ] ) ? array( 'key' => '_nj_lloji', 'value' => $urapress_lloji ) : null,
				isset( $urapress_cats[ $urapress_kat ] ) ? array( 'key' => '_nj_kategoria', 'value' => $urapress_kat ) : null,
			)
		)
	),
);
$urapress_stars = get_posts( $urapress_star_args );

/* Beispiel-Anzeigen: nur solange es kaum echte gibt, klar als «Shembull» markiert */
$urapress_examples = array(
	array( 'kerkoj', 'pune', 'Bern', 'Kërkoj pllakashtrues për 2 ditë punë (banjo)', 'Banjo rreth 6 m², pllakat i kam. Punë në fund të muajit, pagesa e mirë.' ),
	array( 'ofroj', 'sherbime', 'Zürich', 'Ngjyrosje banesash – shpejt dhe pastër', 'Ngjyrosim banesa dhe shtëpi, edhe në fundjavë. Ofertë falas brenda një dite.' ),
	array( 'kerkoj', 'banese', 'Biel', 'Kërkoj banesë 3.5 dhoma afër stacionit', 'Familje me dy fëmijë, punë e qëndrueshme. Nga janari ose shkurti.' ),
	array( 'ofroj', 'vetura', 'Luzern', 'Shes VW Golf 2016, me MFK të re', '98\'000 km, servis i rregullt, gomat e dimrit përfshirë.' ),
	array( 'ofroj', 'shitje', 'Basel', 'Djep fëmijësh pothuajse i ri', 'Përdorur vetëm 6 muaj, me dyshek. Merret në Basel.' ),
	array( 'kerkoj', 'tjera', 'St. Gallen', 'Kërkoj shoqërues për rrugë në Kosovë në dhjetor', 'Nisemi më 20 dhjetor me veturë, ndajmë shpenzimet e rrugës.' ),
);
$urapress_show_examples = ! $urapress_filtered && array_sum( urapress_nj_counts() ) < 6;
?>
<main class="up-wrap up-njs">
	<header class="up-njs__hero">
		<h1 class="up-njs__title">Njoftime</h1>
		<p class="up-njs__sub">Kërkoni ose ofroni diçka brenda komunitetit – punë, zanatçi, banesë, veturë, shërbime. Falas.</p>
		<p class="up-njs__me"><?php if ( is_user_logged_in() ) : ?><a href="<?php echo esc_url( home_url( '/llogaria/' ) ); ?>">👤 Llogaria ime – njoftimet e mia dhe të ruajturat</a><?php else : ?><a href="<?php echo esc_url( urapress_hyr_url( $urapress_base ) ); ?>">👤 Hyr</a> – për të menaxhuar njoftimet tuaja dhe për t'i ruajtur<?php endif; ?></p>
		<p class="up-njs__sub up-njs__sub--de" lang="de">Gratis Kleinanzeigen der albanischen Community in der Schweiz – Handwerker, Wohnung, Auto, Dienstleistungen. Auch auf Deutsch.</p>
		<form class="up-njs__search" method="get" action="<?php echo esc_url( $urapress_base ); ?>" role="search">
			<div class="up-njs__tog">
				<?php foreach ( array( '' => 'Të gjitha' ) + urapress_nj_types() as $k => $v ) : ?>
					<label><input type="radio" name="lloji" value="<?php echo esc_attr( $k ); ?>" <?php checked( $urapress_lloji, $k ); ?> onchange="this.form.submit()"><span><?php echo esc_html( $v ); ?></span></label>
				<?php endforeach; ?>
			</div>
			<?php if ( $urapress_kat ) : ?><input type="hidden" name="kategoria" value="<?php echo esc_attr( $urapress_kat ); ?>"><?php endif; ?>
			<input class="up-njs__q" type="search" name="q" value="<?php echo esc_attr( $urapress_q ); ?>" placeholder="Çfarë kërkon? p.sh. pllakashtrues, banesë në Bern…" aria-label="Kërko në njoftime">
			<button class="up-njs__go" type="submit" aria-label="Kërko"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg></button>
			<a class="up-njs__add" href="#shto">+ Shto njoftim</a>
		</form>
	</header>

	<h2 class="up-njs__h2">Kategoritë</h2>
	<nav class="up-njs__tiles" aria-label="Kategoritë">
		<?php
		foreach ( $urapress_cats as $k => $v ) :
			list( $urapress_bg, $urapress_svg ) = urapress_nj_icon( $k );
			$urapress_url = add_query_arg( array_filter( array( 'kategoria' => $k === $urapress_kat ? false : $k, 'lloji' => $urapress_lloji ?: false, 'q' => $urapress_q ?: false ) ), $urapress_base );
			$urapress_n   = $urapress_counts[ $k ];
			?>
			<a class="up-njs__tile<?php echo $k === $urapress_kat ? ' is-active' : ''; ?>" href="<?php echo esc_url( $urapress_url ); ?>" style="--b:<?php echo esc_attr( $urapress_bg ); ?>">
				<span class="up-njs__pic"><svg viewBox="0 0 120 120" aria-hidden="true"><?php echo $urapress_svg; // phpcs:ignore -- feste Zeichnung ?></svg></span>
				<b><?php echo esc_html( $v ); ?></b>
				<i class="up-njs__de" lang="de"><?php echo esc_html( urapress_nj_cats_de()[ $k ] ); ?></i>
				<small><?php echo esc_html( $urapress_n ? $urapress_n . ' ' . ( 1 === $urapress_n ? 'njoftim' : 'njoftime' ) : 'bëhu i pari' ); ?></small>
			</a>
		<?php endforeach; ?>
	</nav>

	<div class="up-njs__listhead">
		<h2 class="up-njs__h2">
			<?php
			if ( $urapress_q ) {
				echo esc_html( 'Rezultatet për «' . $urapress_q . '»' );
			} elseif ( $urapress_kat && isset( $urapress_cats[ $urapress_kat ] ) ) {
				echo esc_html( $urapress_cats[ $urapress_kat ] );
			} else {
				echo 'Njoftimet e fundit';
			}
			?>
		</h2>
		<?php if ( $urapress_filtered ) : ?><a class="up-section__more" href="<?php echo esc_url( $urapress_base ); ?>">× Hiq filtrat</a><?php endif; ?>
	</div>

	<?php if ( $urapress_stars ) : ?>
		<div class="up-njs__grid up-njs__grid--stars">
			<?php
			foreach ( $urapress_stars as $urapress_p ) {
				urapress_nj_card( $urapress_p );
			}
			?>
		</div>
	<?php endif; ?>

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
	<?php elseif ( ! $urapress_stars && ! $urapress_show_examples ) : ?>
		<p class="up-njs__empty">Ende nuk ka njoftime këtu. Bëhuni i pari – <a href="#shto">shtoni një njoftim</a>.</p>
	<?php endif; ?>

	<?php if ( $urapress_show_examples ) : ?>
		<section class="up-njs__examples">
			<p class="up-njs__exhead"><b>Kështu duket një njoftim.</b> Këta janë shembuj – shtoni të tuajin falas dhe e shohin mijëra shqiptarë në Zvicër.</p>
			<div class="up-njs__grid">
				<?php foreach ( $urapress_examples as $e ) : ?>
					<article class="up-nj up-nj--<?php echo esc_attr( $e[0] ); ?> up-nj--shembull">
						<div class="up-nj__top">
							<span class="up-nj__shembull">Shembull</span>
							<span class="up-nj__lloji"><?php echo esc_html( urapress_nj_types()[ $e[0] ] ); ?></span>
							<span class="up-nj__kat"><?php echo esc_html( $urapress_cats[ $e[1] ] ); ?></span>
							<span class="up-nj__vendi">📍 <?php echo esc_html( $e[2] ); ?></span>
						</div>
						<h3 class="up-nj__titulli"><?php echo esc_html( $e[3] ); ?></h3>
						<p class="up-nj__teksti"><?php echo esc_html( $e[4] ); ?></p>
						<div class="up-nj__fund"><a class="up-nj__btn" href="#shto">+ Shto njoftimin tënd</a></div>
					</article>
				<?php endforeach; ?>
			</div>
		</section>
	<?php endif; ?>

	<section class="up-njs__form" id="shto">
		<h2>Shto njoftim falas</h2>
		<?php if ( ! is_user_logged_in() ) : ?><p class="up-njs__biz">👤 <a href="<?php echo esc_url( urapress_hyr_url( $urapress_base . '#shto' ) ); ?>">Hyni</a> para se ta dërgoni, që ta ndryshoni, rinovoni ose fshini njoftimin vetë më vonë.</p><?php endif; ?>
		<p class="up-njs__note">Njoftimi del pas kontrollit nga redaksia dhe qëndron <?php echo (int) URAPRESS_NJ_DAYS; ?> ditë. Numri juaj i telefonit shfaqet në njoftim që të mund t'ju kontaktojnë.</p>
		<p class="up-njs__biz">⭐ <b>Keni biznes?</b> Një njoftim është falas. Me <b>19 CHF</b> njoftimi juaj del <b>i theksuar në krye</b> për 30 ditë – na shkruani në <a href="https://wa.me/41762411974" target="_blank" rel="noopener">WhatsApp 076 241 19 74</a>.</p>
		<?php if ( isset( $urapress_msgs[ $urapress_msg ] ) ) : ?>
			<p class="up-njs__msg up-njs__msg--<?php echo esc_attr( $urapress_msgs[ $urapress_msg ][0] ); ?>"><?php echo esc_html( $urapress_msgs[ $urapress_msg ][1] ); ?></p>
		<?php endif; ?>
		<form method="post" action="<?php echo esc_url( admin_url( 'admin-post.php' ) ); ?>" enctype="multipart/form-data">
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
						<?php foreach ( $urapress_cats as $k => $v ) : ?>
							<option value="<?php echo esc_attr( $k ); ?>" <?php selected( $urapress_kat, $k ); ?>><?php echo esc_html( $v ); ?></option>
						<?php endforeach; ?>
					</select>
				</label>
				<label>Vendi <input type="text" name="nj_vendi" maxlength="40" placeholder="p.sh. Bern"></label>
			</div>
			<fieldset class="up-njs__car" data-nj-car hidden>
				<legend>🚗 Të dhënat e veturës</legend>
				<div class="up-njs__row3">
					<label>Marka * <input type="text" name="nj_marka" maxlength="30" placeholder="p.sh. VW"></label>
					<label>Modeli * <input type="text" name="nj_modeli" maxlength="40" placeholder="p.sh. Golf 1.4 TSI"></label>
					<label><span data-nj-price>Çmimi (CHF) *</span> <input type="text" name="nj_cmimi" inputmode="numeric" maxlength="9" placeholder="p.sh. 12500"></label>
				</div>
			</fieldset>
			<fieldset class="up-njs__lloji up-njs__numri">
				<legend>Gjuha e njoftimit / Sprache der Anzeige</legend>
				<label><input type="radio" name="nj_gjuha" value="sq" checked> Shqip</label>
				<label><input type="radio" name="nj_gjuha" value="de"> Deutsch</label>
			</fieldset>
			<label>Titulli <input type="text" name="nj_titulli" minlength="5" maxlength="80" required placeholder="p.sh. Kërkoj pllakashtrues për 2 ditë punë (banjo)"></label>
			<label>Teksti <textarea name="nj_teksti" rows="5" minlength="10" maxlength="600" required placeholder="Përshkruani shkurt: çfarë, kur, ku…"></textarea></label>
			<div class="up-njs__row">
				<label>Emri <input type="text" name="nj_emri" maxlength="40" placeholder="p.sh. Arben" value="<?php echo esc_attr( get_user_meta( get_current_user_id(), 'urapress_nj_emri', true ) ); ?>"></label>
				<label>Telefoni / WhatsApp <input type="tel" name="nj_telefoni" required placeholder="079 123 45 67" value="<?php echo esc_attr( get_user_meta( get_current_user_id(), 'urapress_nj_telefoni', true ) ); ?>"></label>
			</div>
			<fieldset class="up-njs__lloji up-njs__numri">
				<legend>Kush e sheh numrin tënd?</legend>
				<label><input type="radio" name="nj_numri" value="te_gjithe" checked> Të gjithë</label>
				<label><input type="radio" name="nj_numri" value="anetaret"> Vetëm anëtarët e kyçur 🔒</label>
			</fieldset>
			<label>Foto (deri në <?php echo (int) URAPRESS_NJ_MAX_FOTO; ?>, falas) <input type="file" name="nj_foto[]" accept="image/jpeg,image/png,image/webp" multiple data-nj-foto></label>
			<p class="up-njs__hint" data-nj-foto-msg>JPG, PNG ose WEBP, maksimum 8 MB secila.</p>
			<label class="up-njs__check"><input type="checkbox" name="nj_pranoj" value="1" required> Pranoj që numri im të shfaqet sipas zgjedhjes sime më lart dhe që redaksia mund ta refuzojë njoftimin.</label>
			<button class="up-btn" type="submit">Dërgo njoftimin</button>
		</form>
	</section>
</main>
<script>
(function () {
	var f = document.querySelector('#shto form');
	if (!f) { return; }
	var box = f.querySelector('[data-nj-car]'), kat = f.querySelector('[name=nj_kategoria]');
	var price = f.querySelector('[data-nj-price]'), foto = f.querySelector('[data-nj-foto]'), msg = f.querySelector('[data-nj-foto-msg]');
	function upd() {
		var car = kat.value === 'vetura';
		box.hidden = !car;
		box.querySelectorAll('input').forEach(function (i) { i.required = car; });
		var kerkoj = (f.querySelector('[name=nj_lloji]:checked') || {}).value === 'kerkoj';
		price.textContent = kerkoj ? 'Buxheti (CHF) *' : 'Çmimi (CHF) *';
	}
	kat.addEventListener('change', upd);
	f.querySelectorAll('[name=nj_lloji]').forEach(function (r) { r.addEventListener('change', upd); });
	upd();
	foto.addEventListener('change', function () {
		if (foto.files.length > <?php echo (int) URAPRESS_NJ_MAX_FOTO; ?>) {
			msg.textContent = 'Maksimum <?php echo (int) URAPRESS_NJ_MAX_FOTO; ?> foto – vetëm të parat merren.';
			msg.classList.add('is-err');
		} else {
			msg.textContent = foto.files.length ? foto.files.length + ' foto të zgjedhura.' : 'JPG, PNG ose WEBP, maksimum 8 MB secila.';
			msg.classList.remove('is-err');
		}
	});
})();
</script>
<?php
get_footer();
