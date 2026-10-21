<?php
/**
 * Ein einzelnes Njoftim.
 *
 * @package UraPress
 */

get_header();
?>
<main class="up-wrap up-njs up-njs--single">
	<p><a class="up-section__more" href="<?php echo esc_url( get_post_type_archive_link( 'njoftim' ) ); ?>">← Të gjitha njoftimet</a></p>
	<?php
	while ( have_posts() ) :
		the_post();
		$urapress_old = ( time() - get_post_time( 'U', true ) ) > URAPRESS_NJ_DAYS * DAY_IN_SECONDS;
		if ( $urapress_old ) :
			?>
			<p class="up-njs__msg up-njs__msg--err">Ky njoftim ka skaduar.</p>
			<?php
		else :
			urapress_nj_card( get_post(), true );
			urapress_share( get_permalink(), get_the_title() . ' – Njoftim në UraPress' );
		endif;
	endwhile;
	?>
</main>
<?php
get_footer();
