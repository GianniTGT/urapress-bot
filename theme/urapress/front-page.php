<?php
/**
 * Faqja kryesore (Ballina).
 *
 * @package UraPress
 */

get_header();

$urapress_top = new WP_Query(
	array(
		'posts_per_page'      => 5,
		'post_status'         => 'publish',
		'ignore_sticky_posts' => false,
	)
);
?>
<main class="up-wrap">

<?php if ( ! $urapress_top->have_posts() ) : ?>
	<div class="up-empty">
		<h1><?php esc_html_e( 'Së shpejti', 'urapress' ); ?></h1>
		<p><?php esc_html_e( 'Lajmet e para po vijnë. Ura mes Atdheut dhe Dijasporës po ngrihet.', 'urapress' ); ?></p>
	</div>
<?php else : ?>

	<section class="up-hero" aria-label="<?php esc_attr_e( 'Lajmet kryesore', 'urapress' ); ?>">
		<?php
		$urapress_i = 0;
		while ( $urapress_top->have_posts() ) :
			$urapress_top->the_post();
			if ( 0 === $urapress_i ) {
				get_template_part(
					'template-parts/card',
					null,
					array(
						'variant' => 'lead',
						'size'    => 'urapress-lead',
						'excerpt' => true,
						'heading' => 'h2',
					)
				);
				echo '<div class="up-hero__side">';
			} else {
				get_template_part( 'template-parts/card' );
			}
			$urapress_i++;
		endwhile;
		echo '</div>';
		wp_reset_postdata();
		?>
	</section>

	<?php
	$urapress_latest = new WP_Query(
		array(
			'posts_per_page'      => 8,
			'post__not_in'        => urapress_shown(),
			'ignore_sticky_posts' => true,
		)
	);
	if ( $urapress_latest->have_posts() ) :
		?>
		<section class="up-section">
			<div class="up-section__head"><h2 class="up-section__title"><?php esc_html_e( 'Të fundit', 'urapress' ); ?></h2></div>
			<div class="up-grid-4">
				<?php
				while ( $urapress_latest->have_posts() ) :
					$urapress_latest->the_post();
					get_template_part( 'template-parts/card' );
				endwhile;
				wp_reset_postdata();
				?>
			</div>
		</section>
	<?php endif; ?>

	<?php if ( is_active_sidebar( 'ads-home' ) ) : ?>
		<section class="up-section"><?php dynamic_sidebar( 'ads-home' ); ?></section>
	<?php endif; ?>

	<?php
	foreach ( urapress_main_categories() as $urapress_name ) :
		$urapress_term = urapress_category_by_name( $urapress_name );
		if ( ! $urapress_term ) {
			continue;
		}
		$urapress_cat_q = new WP_Query(
			array(
				'cat'                 => $urapress_term->term_id,
				'posts_per_page'      => 5,
				'post__not_in'        => urapress_shown(),
				'ignore_sticky_posts' => true,
			)
		);
		if ( ! $urapress_cat_q->have_posts() ) {
			continue;
		}
		?>
		<section class="up-section">
			<div class="up-section__head">
				<h2 class="up-section__title"><a href="<?php echo esc_url( get_category_link( $urapress_term ) ); ?>"><?php echo esc_html( $urapress_term->name ); ?></a></h2>
				<a class="up-section__more" href="<?php echo esc_url( get_category_link( $urapress_term ) ); ?>"><?php esc_html_e( 'Shiko të gjitha', 'urapress' ); ?> →</a>
			</div>
			<div class="up-catblock">
				<?php
				$urapress_j = 0;
				while ( $urapress_cat_q->have_posts() ) :
					$urapress_cat_q->the_post();
					if ( 0 === $urapress_j ) {
						get_template_part( 'template-parts/card', null, array( 'excerpt' => true ) );
						echo '<div class="up-catblock__list">';
					} else {
						get_template_part(
							'template-parts/card',
							null,
							array(
								'variant' => 'row',
								'size'    => 'urapress-thumb',
							)
						);
					}
					$urapress_j++;
				endwhile;
				echo '</div>';
				wp_reset_postdata();
				?>
			</div>
		</section>
	<?php endforeach; ?>

<?php endif; ?>
</main>
<?php
get_footer();
