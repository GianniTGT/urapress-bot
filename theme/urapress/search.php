<?php
/**
 * Rezultatet e kërkimit.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap up-layout">
	<div>
		<header class="up-archive__head">
			<h1 class="up-archive__title">
				<?php
				/* translators: %s: fjala e kërkuar */
				printf( esc_html__( 'Kërkimi: %s', 'urapress' ), '<span>' . esc_html( get_search_query() ) . '</span>' );
				?>
			</h1>
		</header>

		<?php if ( have_posts() ) : ?>
			<div class="up-list">
				<?php
				while ( have_posts() ) :
					the_post();
					get_template_part(
						'template-parts/card',
						null,
						array(
							'excerpt' => true,
							'heading' => 'h2',
						)
					);
				endwhile;
				?>
			</div>
			<div class="up-pagination"><?php echo paginate_links( array( 'prev_text' => '‹', 'next_text' => '›' ) ); // phpcs:ignore ?></div>
		<?php else : ?>
			<p><?php esc_html_e( 'Nuk u gjet asnjë lajm. Provo një fjalë tjetër.', 'urapress' ); ?></p>
			<?php get_search_form(); ?>
		<?php endif; ?>
	</div>
	<?php get_sidebar(); ?>
</main>
<?php
get_footer();
