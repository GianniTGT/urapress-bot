<?php
/**
 * Shiriti anësor.
 *
 * @package UraPress
 */
?>
<aside class="up-sidebar" aria-label="<?php esc_attr_e( 'Shiriti anësor', 'urapress' ); ?>">
	<?php if ( is_active_sidebar( 'sidebar-1' ) ) : ?>
		<?php dynamic_sidebar( 'sidebar-1' ); ?>
	<?php else : ?>
		<section class="up-widget">
			<div class="up-section__head"><h2 class="up-section__title"><?php esc_html_e( 'Të fundit', 'urapress' ); ?></h2></div>
			<div class="up-catblock__list">
				<?php
				$urapress_side = new WP_Query(
					array(
						'posts_per_page'      => 6,
						'post__not_in'        => is_singular() ? array( get_queried_object_id() ) : array(),
						'ignore_sticky_posts' => true,
					)
				);
				while ( $urapress_side->have_posts() ) :
					$urapress_side->the_post();
					get_template_part(
						'template-parts/card',
						null,
						array(
							'variant' => 'row',
							'size'    => 'urapress-thumb',
						)
					);
				endwhile;
				wp_reset_postdata();
				?>
			</div>
		</section>

		<?php
		foreach ( urapress_pick_ads( 1 ) as $urapress_ad ) {
			urapress_render_ad( $urapress_ad );
		}
		$urapress_ad_page = get_page_by_path( 'reklamo' );
		?>
		<div class="up-ad up-ad--small">
			<strong><?php esc_html_e( 'Reklamoni biznesin tuaj këtu', 'urapress' ); ?></strong><br>
			<a class="up-section__more" href="<?php echo esc_url( $urapress_ad_page ? get_permalink( $urapress_ad_page ) : 'mailto:redaksia@urapress.ch' ); ?>"><?php esc_html_e( 'Më shumë', 'urapress' ); ?> →</a>
		</div>
	<?php endif; ?>
</aside>
