<?php
/**
 * Faqet statike (Rreth nesh, Kontakt, Impressum …).
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap">
	<?php
	while ( have_posts() ) :
		the_post();
		?>
		<article id="post-<?php the_ID(); ?>" <?php post_class( 'up-page' ); ?>>
			<h1 class="up-article__title"><?php the_title(); ?></h1>
			<div class="up-content"><?php the_content(); ?></div>
		</article>
	<?php endwhile; ?>
</main>
<?php
get_footer();
