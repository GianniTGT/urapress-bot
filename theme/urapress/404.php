<?php
/**
 * Faqja nuk u gjet.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap">
	<div class="up-empty">
		<h1><?php esc_html_e( 'Kjo faqe nuk u gjet', 'urapress' ); ?></h1>
		<p><?php esc_html_e( 'Ndoshta lidhja është e vjetër. Provo të kërkosh lajmin:', 'urapress' ); ?></p>
		<?php get_search_form(); ?>
		<p style="margin-top:24px"><a class="up-section__more" href="<?php echo esc_url( home_url( '/' ) ); ?>">← <?php esc_html_e( 'Kthehu në Ballinë', 'urapress' ); ?></a></p>
	</div>
</main>
<?php
get_footer();
