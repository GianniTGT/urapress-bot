<?php
/**
 * Artikulli i vetëm.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap up-layout">
	<div>
	<?php
	while ( have_posts() ) :
		the_post();
		$urapress_cat   = urapress_primary_category();
		$urapress_thumb = get_post_thumbnail_id();
		$urapress_url   = rawurlencode( get_permalink() );
		$urapress_title = rawurlencode( get_the_title() );
		$urapress_zazu  = in_category( 'zazu' );
		if ( $urapress_zazu ) {
			$urapress_thumb = 0; // Comic steht ganz im Text, nicht als zugeschnittenes Titelbild
		}
		?>
		<article id="post-<?php the_ID(); ?>" <?php post_class( 'up-article' ); ?>>
			<header>
				<?php if ( $urapress_cat ) : ?>
					<a class="up-article__cat" href="<?php echo esc_url( get_category_link( $urapress_cat ) ); ?>"><?php echo esc_html( $urapress_cat->name ); ?></a>
				<?php endif; ?>
				<h1 class="up-article__title"><?php the_title(); ?></h1>
				<?php if ( has_excerpt() ) : ?>
					<p class="up-article__lead"><?php echo esc_html( get_the_excerpt() ); ?></p>
				<?php endif; ?>
				<div class="up-article__meta">
					<span><?php echo esc_html( get_the_author() ?: __( 'Redaksia', 'urapress' ) ); ?></span>
					<span><?php echo esc_html( urapress_sq_date( (int) get_post_time( 'U' ), false, true ) ); ?></span>
				</div>
			</header>

			<?php if ( $urapress_thumb ) : ?>
				<figure class="up-article__figure">
					<?php the_post_thumbnail( 'urapress-lead', array( 'loading' => 'eager' ) ); ?>
					<?php
					$urapress_caption = wp_get_attachment_caption( $urapress_thumb );
					if ( $urapress_caption ) :
						?>
						<figcaption class="<?php echo urapress_is_ai_image( $urapress_thumb ) ? 'is-ai' : ''; ?>"><?php echo esc_html( $urapress_caption ); ?></figcaption>
					<?php endif; ?>
				</figure>
			<?php endif; ?>

			<div class="up-content">
				<?php the_content(); ?>
			</div>

			<?php if ( $urapress_zazu ) : ?>
				<nav class="up-zazu-nav" aria-label="ZaZu">
					<?php
					$urapress_older = get_previous_post( true );
					$urapress_newer = get_next_post( true );
					echo $urapress_older ? '<a href="' . esc_url( get_permalink( $urapress_older ) ) . '">← ZaZu i mëparshëm</a>' : '<span></span>';
					echo '<a href="' . esc_url( get_category_link( urapress_zazu_cat_id() ) ) . '">Të gjitha</a>';
					echo $urapress_newer ? '<a href="' . esc_url( get_permalink( $urapress_newer ) ) . '">ZaZu i radhës →</a>' : '<span></span>';
					?>
				</nav>
			<?php endif; ?>

			<?php
			$urapress_tags = get_the_tags();
			if ( $urapress_tags ) :
				?>
				<div class="up-tags">
					<?php foreach ( $urapress_tags as $urapress_tag ) : ?>
						<a href="<?php echo esc_url( get_tag_link( $urapress_tag ) ); ?>">#<?php echo esc_html( $urapress_tag->name ); ?></a>
					<?php endforeach; ?>
				</div>
			<?php endif; ?>

			<?php
			if ( ! $urapress_zazu ) {
				urapress_nj_promo();
			}
			?>

			<div class="up-share" aria-label="<?php esc_attr_e( 'Shpërndaje', 'urapress' ); ?>">
				<a class="up-share__wa" href="https://wa.me/?text=<?php echo $urapress_title . '%20' . $urapress_url; // phpcs:ignore ?>" target="_blank" rel="noopener">WhatsApp</a>
				<a class="up-share__fb" href="https://www.facebook.com/sharer/sharer.php?u=<?php echo $urapress_url; // phpcs:ignore ?>" target="_blank" rel="noopener">Facebook</a>
				<a class="up-share__x" href="https://twitter.com/intent/tweet?url=<?php echo $urapress_url; // phpcs:ignore ?>&amp;text=<?php echo $urapress_title; // phpcs:ignore ?>" target="_blank" rel="noopener">X</a>
			</div>
		</article>

		<?php
		foreach ( urapress_pick_ads( 1 ) as $urapress_ad ) {
			urapress_render_ad( $urapress_ad, 'wide' );
		}
		if ( comments_open() || get_comments_number() ) {
			comments_template();
		}
		if ( $urapress_cat ) :
			$urapress_related = new WP_Query(
				array(
					'cat'                 => $urapress_cat->term_id,
					'posts_per_page'      => 3,
					'post__not_in'        => array( get_the_ID() ),
					'ignore_sticky_posts' => true,
				)
			);
			if ( $urapress_related->have_posts() ) :
				?>
				<section class="up-section up-related">
					<div class="up-section__head"><h2 class="up-section__title"><?php esc_html_e( 'Lexo edhe', 'urapress' ); ?></h2></div>
					<div class="up-grid-3">
						<?php
						while ( $urapress_related->have_posts() ) :
							$urapress_related->the_post();
							get_template_part( 'template-parts/card' );
						endwhile;
						wp_reset_postdata();
						?>
					</div>
				</section>
				<?php
			endif;
		endif;
	endwhile;
	?>
	</div>
	<?php get_sidebar(); ?>
</main>
<?php
get_footer();
