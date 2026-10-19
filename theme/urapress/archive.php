<?php
/**
 * Rubrikat, etiketat dhe arkivat.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap up-layout">
	<div>
		<header class="up-archive__head">
			<h1 class="up-archive__title"><?php echo esc_html( single_term_title( '', false ) ?: wp_strip_all_tags( get_the_archive_title() ) ); ?></h1>
			<?php the_archive_description( '<div class="up-archive__desc">', '</div>' ); ?>
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
			<div class="up-pagination">
				<?php
				echo paginate_links( // phpcs:ignore
					array(
						'prev_text' => '‹',
						'next_text' => '›',
						'mid_size'  => 1,
					)
				);
				?>
			</div>
		<?php else : ?>
			<p><?php esc_html_e( 'Ende nuk ka lajme në këtë rubrikë.', 'urapress' ); ?></p>
		<?php endif; ?>
	</div>
	<?php get_sidebar(); ?>
</main>
<?php
get_footer();
